#!/usr/bin/env python3
"""Read it For Me (RIFM) local server: serves the app and runs the free Kokoro AI voice on this machine.

Start it with:  ./start.sh  (macOS/Linux)  or  start.bat  (Windows)
                or double-click "Read it For Me.command" (macOS) / "Read it For Me.bat" (Windows)
Then open:      http://127.0.0.1:8787

Environment variables:
  RIFM_PORT   port to listen on (default 8787)
  RIFM_MODEL  path to the Kokoro .onnx model   (default models/kokoro-v1.0.onnx)
  RIFM_VOICES path to the Kokoro voices file   (default models/voices-v1.0.bin)
"""
import http.client
import io
import ipaddress
import json
import os
import re
import socket
import ssl
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("RIFM_PORT", "8787"))
MODEL = Path(os.environ.get("RIFM_MODEL", HERE / "models" / "kokoro-v1.0.onnx"))
VOICES = Path(os.environ.get("RIFM_VOICES", HERE / "models" / "voices-v1.0.bin"))
MAX_TEXT = 500           # characters per request (the app sends sentences of at most ~140)
MAX_BODY = 64 * 1024     # bytes
MAX_PAGE = 15 * 1024 * 1024   # largest web page / PDF the app will download from a link

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


# ================= Reading web links =================
# The browser page cannot download other websites itself, so the server does it, carefully:
# only public http(s) addresses (never this computer or the home network), size and time limits.
class FetchError(Exception):
    """A problem with a link, explained in plain words for the app to show."""


PAGE_TYPES = {"text/html": "html", "application/xhtml+xml": "html", "text/plain": "text",
              "text/markdown": "text", "application/pdf": "pdf"}
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0 Safari/537.36 ReadItForMe/1.1")


def public_address(host: str, port: int) -> str:
    """The IP address to connect to, refusing anything that is not on the public internet."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError):
        raise FetchError(f"Could not find the website {host}. Check the link and your internet connection.") from None
    for *_, addr in infos:
        ip = ipaddress.ip_address(addr[0].split("%")[0])
        ip = getattr(ip, "ipv4_mapped", None) or ip
        if not ip.is_global:
            raise FetchError("For safety, links to this computer or your home network can't be opened.")
    return infos[0][4][0]


class _PinnedHTTP(http.client.HTTPConnection):
    """Connects to the address that was checked, so DNS can't swap in a private one afterwards."""

    def __init__(self, host, ip, port, timeout):
        super().__init__(host, port, timeout=timeout)
        self._ip = ip

    def connect(self):
        self.sock = socket.create_connection((self._ip, self.port), self.timeout)


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, ip, port, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._ip = ip

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def fetch_page(url: str, timeout: float = 20) -> tuple[str, str, bytes]:
    """Download a public web page or PDF. Returns (final URL, kind, body); kind is html, text or pdf."""
    url = url.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*://", url, re.I):
        if re.match(r"^[a-z][a-z0-9+-]*:(?!\d)", url, re.I):     # javascript:, mailto:, data:…
            raise FetchError("Only web links that start with http:// or https:// can be read.")
        url = "https://" + url                      # "example.com/page" → "https://example.com/page"
    for _ in range(6):                              # follow up to 5 redirects, checking each one
        u = urllib.parse.urlsplit(url)
        if u.scheme.lower() not in ("http", "https") or not u.hostname:
            raise FetchError("Only web links that start with http:// or https:// can be read.")
        if u.username or u.password:
            raise FetchError("Links with a user name or password in them can't be opened.")
        https = u.scheme.lower() == "https"
        try:
            port = u.port or (443 if https else 80)
        except ValueError:
            raise FetchError("That link has an invalid port number.") from None
        if port not in (80, 443, 8080, 8443):
            raise FetchError("Only links to normal web ports can be opened.")
        ip = public_address(u.hostname, port)
        conn = (_PinnedHTTPS if https else _PinnedHTTP)(u.hostname, ip, port, timeout)
        path = urllib.parse.urlunsplit(("", "", u.path or "/", u.query, ""))
        try:
            conn.request("GET", path, headers={
                "User-Agent": BROWSER_UA, "Accept-Language": "en,*;q=0.5", "Accept-Encoding": "identity",
                "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain;q=0.9,*/*;q=0.5",
            })
            r = conn.getresponse()
            location = r.getheader("Location")
            if r.status in (301, 302, 303, 307, 308) and location:
                url = urllib.parse.urljoin(url, location)
                continue
            if r.status in (401, 403):
                raise FetchError(f"The website refused (error {r.status}). It may need a login or block apps "
                                 "like this one. Open it in your browser, copy the text and paste it here instead.")
            if r.status == 404:
                raise FetchError("That page doesn't exist (error 404). Check the link.")
            if r.status >= 400:
                raise FetchError(f"The website answered with error {r.status}. Try again later.")
            ctype = (r.getheader("Content-Type") or "text/html").split(";")[0].strip().lower()
            kind = PAGE_TYPES.get(ctype)
            if not kind:
                raise FetchError(f"That link is a {ctype} file, which can't be read aloud.")
            if int(r.getheader("Content-Length") or 0) > MAX_PAGE:
                raise FetchError("That page is too large to read.")
            body = r.read(MAX_PAGE + 1)
            if len(body) > MAX_PAGE:
                raise FetchError("That page is too large to read.")
            if kind != "pdf":
                body = decode_page(body, r.getheader("Content-Type") or "").encode()
            return url, kind, body
        except TimeoutError:
            raise FetchError("The website took too long to answer. Try again later.") from None
        except ssl.SSLError:
            raise FetchError("The website's security certificate could not be checked.") from None
        except (OSError, http.client.HTTPException) as e:
            raise FetchError(f"Could not download the page ({type(e).__name__}).") from None
        finally:
            conn.close()
    raise FetchError("That link redirects too many times.")


def decode_page(body: bytes, content_type: str) -> str:
    """Bytes → text, using the charset from the header or the page's own <meta> tag."""
    m = re.search(r"charset=[\"']?([\w.:-]+)", content_type, re.I) or \
        re.search(rb"<meta[^>]+charset=[\"']?([\w.:-]+)", body[:4096], re.I)
    charset = m.group(1) if m else "utf-8"
    charset = charset.decode("ascii", "ignore") if isinstance(charset, bytes) else charset
    try:
        return body.decode(charset, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


def load_model():
    global kokoro, VOICE_IDS
    missing = [p for p in (MODEL, VOICES) if not p.is_file()]
    if missing:
        sys.exit("❌ Kokoro model files are missing:\n   " + "\n   ".join(map(str, missing)) +
                 "\n   Run setup first: setup.bat (Windows) or ./setup.sh (macOS/Linux).")
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
    server_version = "RIFM/1.0"

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    # ---- helpers ----
    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None):
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
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

    def _from_this_app(self) -> bool:
        """Accept only requests made to this server by its own page (or by non-browser tools).

        Other websites open in the browser must not be able to use the voice. The Host check
        also blocks "DNS rebinding", where a website points its own name at 127.0.0.1."""
        port = self.server.server_address[1]
        ours = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host", "") not in ours:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in {"http://" + h for h in ours}

    # ---- routes ----
    def do_OPTIONS(self):
        self._json(403, {"error": "forbidden"})   # cross-site requests are not allowed

    def do_GET(self):
        if not self._from_this_app():
            return self._json(403, {"error": "forbidden"})
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            return self._json(200, {"app": "rifm", "kokoro": kokoro is not None, "voices": VOICE_IDS})
        if path in STATIC:
            rel, ctype = STATIC[path]
            try:
                return self._send(200, (HERE / rel).read_bytes(), ctype)
            except FileNotFoundError:
                pass
        self._json(404, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self):
        if not self._from_this_app():
            return self._json(403, {"error": "forbidden"})
        if self.path.split("?", 1)[0] == "/api/fetch":
            return self._fetch()
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
        except (ValueError, TypeError):   # includes invalid JSON
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


    def _fetch(self):
        """Download a web link for the app: JSON {url, kind, text} for pages, the raw file for PDFs."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return self._json(400, {"error": "bad request size"})
            url = str(json.loads(self.rfile.read(length)).get("url", ""))[:4000]
        except (ValueError, TypeError, AttributeError):
            return self._json(400, {"error": "invalid JSON"})
        try:
            final, kind, body = fetch_page(url)
        except FetchError as e:
            return self._json(422, {"error": str(e)})
        if kind == "pdf":
            return self._send(200, body, "application/pdf", {"X-Final-Url": urllib.parse.quote(final, safe=":/?&=#%")})
        self._json(200, {"url": final, "kind": kind, "text": body.decode()})


def already_running(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/api/status", timeout=1) as r:
            return json.load(r).get("app") == "rifm"
    except Exception:  # noqa: BLE001
        return False


class Server(ThreadingHTTPServer):
    daemon_threads = True
    # On Windows, address reuse lets two programs share one port silently, so turn it off there
    allow_reuse_address = os.name != "nt"


def main():
    for stream in (sys.stdout, sys.stderr):      # emoji-safe output on older Windows consoles
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    url = f"http://127.0.0.1:{PORT}"
    open_browser = "--no-browser" not in sys.argv
    if already_running(url):
        print(f"Read it For Me is already running at {url}", flush=True)
        if open_browser:
            webbrowser.open(url)
        return
    try:
        srv = Server(("127.0.0.1", PORT), Handler)   # only reachable from this computer
    except OSError:
        tip = "set RIFM_PORT=8788 && start.bat" if os.name == "nt" else "RIFM_PORT=8788 ./start.sh"
        sys.exit(f"❌ Port {PORT} is used by another program. Try: {tip}")
    load_model()
    print(f"✅ Read it For Me is running at {url}   (close this window or press Ctrl+C to quit)", flush=True)
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
