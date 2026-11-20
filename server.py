#!/usr/bin/env python3
"""Read Aloud local server: serves the app and runs the free Kokoro AI voice on this machine.

Start it with:  ./start.sh   (or double-click "Read Aloud.command" on macOS)
Then open:      http://127.0.0.1:8787

Environment variables:
  READ_ALOUD_PORT   port to listen on (default 8787)
  READ_ALOUD_MODEL  path to the Kokoro .onnx model   (default models/kokoro-v1.0.onnx)
  READ_ALOUD_VOICES path to the Kokoro voices file   (default models/voices-v1.0.bin)
"""
import io
import json
import os
import sys
import threading
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("READ_ALOUD_PORT", "8787"))
MODEL = Path(os.environ.get("READ_ALOUD_MODEL", HERE / "models" / "kokoro-v1.0.onnx"))
VOICES = Path(os.environ.get("READ_ALOUD_VOICES", HERE / "models" / "voices-v1.0.bin"))
MAX_TEXT = 1000          # characters per request (the app sends one sentence at a time)
MAX_BODY = 64 * 1024     # bytes

# Files the server is allowed to hand out (nothing else in the folder is exposed)
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/vendor/pdf.min.js": ("vendor/pdf.min.js", "text/javascript"),
    "/vendor/pdf.worker.min.js": ("vendor/pdf.worker.min.js", "text/javascript"),
    "/vendor/mammoth.browser.min.js": ("vendor/mammoth.browser.min.js", "text/javascript"),
}

# First letter of a Kokoro voice id → language used for pronunciation
LANGS = {"a": "en-us", "b": "en-gb", "e": "es", "f": "fr-fr", "h": "hi",
         "i": "it", "j": "ja", "p": "pt-br", "z": "cmn"}
DEFAULT_VOICE = "af_heart"

kokoro = None
VOICE_IDS: list[str] = []
latest_gen: dict[str, int] = {}    # client id → newest playback generation seen
gen_lock = threading.Lock()


class Scheduler:
    """Runs one synthesis at a time, always picking the most urgent waiting request:
    the newest playback first, then the earliest sentence. (A plain Lock wakes waiters
    in random order, which could make the next sentence wait behind later ones.)"""

    def __init__(self):
        self._cond = threading.Condition()
        self._busy = False
        self._waiting: list[tuple] = []
        self._seq = 0

    def run(self, gen: int, index: int, fn):
        with self._cond:
            self._seq += 1
            key = (-gen, index, self._seq)
            self._waiting.append(key)
            while self._busy or min(self._waiting) != key:
                self._cond.wait()
            self._waiting.remove(key)
            self._busy = True
        try:
            return fn()
        finally:
            with self._cond:
                self._busy = False
                self._cond.notify_all()


scheduler = Scheduler()


def load_model():
    global kokoro, VOICE_IDS
    missing = [p for p in (MODEL, VOICES) if not p.is_file()]
    if missing:
        sys.exit("❌ Kokoro model files are missing:\n   " + "\n   ".join(map(str, missing)) +
                 "\n   Run ./setup.sh first.")
    from kokoro_onnx import Kokoro
    print("Loading Kokoro voice model…", flush=True)
    kokoro = Kokoro(str(MODEL), str(VOICES))
    VOICE_IDS = sorted(kokoro.get_voices())
    synthesize("Ready.", DEFAULT_VOICE, 1.0)   # warm-up so the first real sentence is fast


def synthesize(text: str, voice: str, speed: float) -> bytes:
    import soundfile as sf
    samples, rate = kokoro.create(text, voice=voice, speed=speed, lang=LANGS.get(voice[0], "en-us"))
    buf = io.BytesIO()
    sf.write(buf, samples, rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def is_stale(client: str, gen: int) -> bool:
    """True if this client has since started a newer playback (e.g. switched files)."""
    if not client:
        return False
    with gen_lock:
        return gen < latest_gen.get(client, gen)


def note_gen(client: str, gen: int) -> None:
    if not client:
        return
    with gen_lock:
        if len(latest_gen) > 1000:
            latest_gen.clear()
        latest_gen[client] = max(gen, latest_gen.get(client, gen))


class Handler(BaseHTTPRequestHandler):
    server_version = "ReadAloud/1.0"

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    # ---- helpers ----
    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None):
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Content-Type-Options", "nosniff")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass   # the browser cancelled the request (e.g. user pressed Stop)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj).encode(), "application/json")

    # ---- routes ----
    def do_OPTIONS(self):
        self._send(204, b"", "text/plain", {
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        })

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            return self._json(200, {"app": "read-aloud", "kokoro": kokoro is not None, "voices": VOICE_IDS})
        if path in STATIC:
            rel, ctype = STATIC[path]
            try:
                return self._send(200, (HERE / rel).read_bytes(), ctype)
            except FileNotFoundError:
                pass
        self._json(404, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/kokoro":
            return self._json(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return self._json(413 if length > MAX_BODY else 400, {"error": "bad request size"})
            body = json.loads(self.rfile.read(length))
            text = " ".join(str(body.get("text", "")).split())[:MAX_TEXT]
            voice = body.get("voice") if body.get("voice") in VOICE_IDS else DEFAULT_VOICE
            speed = min(max(float(body.get("speed", 1.0)), 0.5), 2.0)
            client = str(body.get("client", ""))[:64]
            gen = int(body.get("gen", 0))
            index = int(body.get("index", 0))
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._json(400, {"error": "invalid JSON"})
        if not text:
            return self._json(400, {"error": "no text"})

        note_gen(client, gen)

        def work():
            if is_stale(client, gen):          # user moved on while this was queued: skip the work
                return None
            return synthesize(text, voice, speed)

        try:
            wav = scheduler.run(gen, index, work)
        except Exception as e:  # noqa: BLE001 — report any model error to the app
            print(f"⚠ Kokoro failed on {text[:60]!r}: {e}", file=sys.stderr, flush=True)
            return self._json(500, {"error": f"Kokoro could not read this sentence: {e}"[:300]})
        if wav is None:
            return self._json(409, {"error": "stale"})
        self._send(200, wav, "audio/wav")


def already_running(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/api/status", timeout=1) as r:
            return json.load(r).get("app") == "read-aloud"
    except Exception:  # noqa: BLE001
        return False


def main():
    url = f"http://127.0.0.1:{PORT}"
    open_browser = "--no-browser" not in sys.argv
    if already_running(url):
        print(f"Read Aloud is already running at {url}", flush=True)
        if open_browser:
            webbrowser.open(url)
        return
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)   # only reachable from this computer
    except OSError:
        sys.exit(f"❌ Port {PORT} is used by another program. Try: READ_ALOUD_PORT=8788 ./start.sh")
    srv.daemon_threads = True
    load_model()
    print(f"✅ Read Aloud is running at {url}   (close this window or press Ctrl+C to quit)", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
