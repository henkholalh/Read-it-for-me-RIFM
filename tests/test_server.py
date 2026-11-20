"""Server tests. Run:  .venv/bin/python -m unittest discover tests -v"""
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import server  # noqa: E402

HAVE_MODEL = server.MODEL.is_file() and server.VOICES.is_file()


class StaleLogicTest(unittest.TestCase):
    def test_newer_generation_makes_older_stale(self):
        server.note_gen("c1", 3)
        self.assertFalse(server.is_stale("c1", 3))
        server.note_gen("c1", 4)
        self.assertTrue(server.is_stale("c1", 3))
        self.assertFalse(server.is_stale("c2", 1))   # other tabs are independent
        self.assertFalse(server.is_stale("", 0))      # no client id → never stale


class SchedulerTest(unittest.TestCase):
    def test_runs_earliest_sentence_of_newest_playback_first(self):
        sch, order, gate = server.Scheduler(), [], threading.Event()
        blocker = threading.Thread(target=sch.run, args=(1, 0, gate.wait))
        blocker.start()
        while not sch._busy:
            pass
        jobs = [(1, 5), (1, 2), (2, 9), (1, 3), (2, 4)]       # (gen, sentence index)
        threads = [threading.Thread(target=sch.run, args=(g, i, lambda g=g, i=i: order.append((g, i)))) for g, i in jobs]
        for t in threads:
            t.start()
        while len(sch._waiting) < len(jobs):
            pass
        gate.set()
        for t in threads + [blocker]:
            t.join()
        self.assertEqual(order, [(2, 4), (2, 9), (1, 2), (1, 3), (1, 5)])


@unittest.skipUnless(HAVE_MODEL, "Kokoro model not downloaded (run ./setup.sh)")
class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.load_model()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def req(self, path, data=None, raw=None):
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        r = urllib.request.Request(self.base + path, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, resp.headers.get("Content-Type"), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type"), e.read()

    def test_status(self):
        code, _, body = self.req("/api/status")
        info = json.loads(body)
        self.assertEqual(code, 200)
        self.assertTrue(info["kokoro"])
        self.assertIn("am_michael", info["voices"])

    def test_serves_app_and_vendor_files(self):
        for path in ["/", "/index.html", "/vendor/pdf.min.js", "/vendor/pdf.worker.min.js", "/vendor/mammoth.browser.min.js"]:
            code, _, body = self.req(path)
            self.assertEqual(code, 200, path)
            self.assertGreater(len(body), 1000, path)

    def test_does_not_expose_other_files(self):
        for path in ["/server.py", "/../server.py", "/models/voices-v1.0.bin", "/.venv/pyvenv.cfg", "/%2e%2e/server.py"]:
            self.assertEqual(self.req(path)[0], 404, path)

    def test_speech_is_wav(self):
        code, ctype, body = self.req("/api/kokoro", {"text": "Hello there, friend.", "voice": "am_michael"})
        self.assertEqual(code, 200)
        self.assertEqual(ctype, "audio/wav")
        self.assertEqual(body[:4], b"RIFF")
        self.assertGreater(len(body), 20000)

    def test_unknown_voice_falls_back(self):
        self.assertEqual(self.req("/api/kokoro", {"text": "Hi.", "voice": "nope"})[0], 200)

    def test_bad_requests(self):
        self.assertEqual(self.req("/api/kokoro", raw=b"{not json")[0], 400)
        self.assertEqual(self.req("/api/kokoro", {"text": "   "})[0], 400)
        self.assertEqual(self.req("/api/kokoro", {"text": "hi", "speed": "fast"})[0], 400)
        self.assertEqual(self.req("/api/kokoro", raw=b"x" * (server.MAX_BODY + 1))[0], 413)
        self.assertEqual(self.req("/api/nothing", {"text": "hi"})[0], 404)

    def test_stale_request_is_skipped(self):
        self.req("/api/kokoro", {"text": "New.", "client": "tab", "gen": 9})
        self.assertEqual(self.req("/api/kokoro", {"text": "Old.", "client": "tab", "gen": 8})[0], 409)

    def test_long_and_odd_text(self):
        for text in ["word " * 400, "1,234.56 — $99 & 50% off!!! ???", "Café naïve résumé 😀"]:
            self.assertEqual(self.req("/api/kokoro", {"text": text})[0], 200, text[:30])


if __name__ == "__main__":
    unittest.main()
