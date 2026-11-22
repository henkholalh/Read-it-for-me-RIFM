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
        threads = [
            threading.Thread(target=sch.run, args=(g, i, lambda g=g, i=i: order.append((g, i))))
            for g, i in jobs
        ]
        for t in threads:
            t.start()
        while len(sch._waiting) < len(jobs):
            pass
        gate.set()
        for t in threads + [blocker]:
            t.join()
        self.assertEqual(order, [(2, 4), (2, 9), (1, 2), (1, 3), (1, 5)])


class OnlyThisAppTest(unittest.TestCase):
    """Other websites open in the browser must not be able to use the local server."""

    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def req(self, path, method="GET", headers=None):
        r = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method, headers=headers or {},
                                   data=b'{"text": "hi"}' if method == "POST" else None)
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                return resp.status, resp.headers
        except urllib.error.HTTPError as e:
            return e.code, e.headers

    def test_own_page_is_allowed(self):
        for host in (f"127.0.0.1:{self.port}", f"localhost:{self.port}"):
            code, headers = self.req("/api/status", headers={"Host": host, "Origin": f"http://{host}"})
            self.assertEqual(code, 200, host)
            self.assertIsNone(headers.get("Access-Control-Allow-Origin"))

    def test_other_websites_are_refused(self):
        for origin in ("https://example.com", "null", f"http://127.0.0.1:{self.port + 1}"):
            self.assertEqual(self.req("/api/kokoro", "POST", {"Origin": origin})[0], 403, origin)
            self.assertEqual(self.req("/api/status", headers={"Origin": origin})[0], 403, origin)
        self.assertEqual(self.req("/api/kokoro", "OPTIONS")[0], 403)

    def test_dns_rebinding_is_refused(self):
        self.assertEqual(self.req("/", headers={"Host": f"evil.example:{self.port}"})[0], 403)
        self.assertEqual(self.req("/api/kokoro", "POST", {"Host": "evil.example"})[0], 403)


class WebLinkTest(unittest.TestCase):
    """Reading web links: safety checks, redirects, types and sizes, without needing the internet."""

    @classmethod
    def setUpClass(cls):
        from http.server import BaseHTTPRequestHandler

        class Site(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                routes = {
                    "/page": (200, "text/html; charset=iso-8859-1", "<p>Caf\xe9 cr\xe8me</p>".encode("latin-1")),
                    "/meta": (200, "text/html", '<meta charset="windows-1252"><p>\x93quoted\x94</p>'.encode("latin-1")),
                    "/doc.pdf": (200, "application/pdf", b"%PDF-1.4 fake"),
                    "/notes.txt": (200, "text/plain; charset=utf-8", b"Just text"),
                    "/image.png": (200, "image/png", b"\x89PNG"),
                    "/big": (200, "text/html", b"x" * (server.MAX_PAGE + 10)),
                    "/locked": (403, "text/html", b"no"),
                    "/gone": (404, "text/html", b"no"),
                }
                if self.path == "/move":
                    self.send_response(302)
                    self.send_header("Location", "/page")
                    self.end_headers()
                    return
                if self.path == "/loop":
                    self.send_response(302)
                    self.send_header("Location", "/loop")
                    self.end_headers()
                    return
                code, ctype, body = routes.get(self.path, (404, "text/plain", b""))
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        cls.site = ThreadingHTTPServer(("127.0.0.1", 0), Site)
        cls.site_port = cls.site.server_address[1]
        threading.Thread(target=cls.site.serve_forever, daemon=True).start()
        # The test site lives on this computer, which the real check refuses; let it through for these tests
        cls.real_check = server.public_address
        server.public_address = lambda host, port: "127.0.0.1"

    @classmethod
    def tearDownClass(cls):
        server.public_address = cls.real_check
        cls.site.shutdown()
        cls.site.server_close()

    def fetch(self, path):
        # The test site uses a random port, which fetch_page would refuse; reach it through port 8080 instead
        real_conn = server._PinnedHTTP.__init__
        port = self.site_port

        def init(conn, host, ip, _port, timeout):
            real_conn(conn, host, ip, port, timeout)
        server._PinnedHTTP.__init__ = init
        try:
            return server.fetch_page(f"http://site.test:8080{path}")
        finally:
            server._PinnedHTTP.__init__ = real_conn

    def test_page_text_is_decoded(self):
        url, kind, body = self.fetch("/page")
        self.assertEqual((kind, body.decode()), ("html", "<p>Café crème</p>"))
        self.assertIn("“quoted”", self.fetch("/meta")[2].decode())   # charset from the page's <meta>
        self.assertEqual(self.fetch("/notes.txt")[1:], ("text", b"Just text"))

    def test_pdf_is_passed_through(self):
        self.assertEqual(self.fetch("/doc.pdf")[1:], ("pdf", b"%PDF-1.4 fake"))

    def test_redirects_are_followed_but_not_forever(self):
        url, kind, body = self.fetch("/move")
        self.assertTrue(url.endswith("/page"))
        with self.assertRaisesRegex(server.FetchError, "redirects too many"):
            self.fetch("/loop")

    def test_clear_errors(self):
        for path, words in [("/image.png", "image/png"), ("/big", "too large"), ("/locked", "login"), ("/gone", "404")]:
            with self.assertRaisesRegex(server.FetchError, words, msg=path):
                self.fetch(path)


class WebLinkSafetyTest(unittest.TestCase):
    """Links must never reach this computer, the home network or non-web services."""

    def test_refused(self):
        cases = {
            "http://127.0.0.1/": "this computer", "http://localhost/": "this computer",
            "http://[::1]/": "this computer", "http://10.0.0.1/": "this computer",
            "http://192.168.1.1/": "this computer", "http://169.254.169.254/latest/": "this computer",
            "http://[::ffff:127.0.0.1]/": "this computer", "http://0.0.0.0/": "this computer",
            "file:///etc/passwd": "http", "ftp://example.com/": "http", "javascript:alert(1)": "http",
            "https://user:pw@example.com/": "password", "https://example.com:22/": "port",
            "https://example.com:99999/": "port",
        }
        for url, words in cases.items():
            with self.assertRaisesRegex(server.FetchError, words, msg=url):
                server.fetch_page(url)

    def test_endpoint_reports_errors_and_refuses_other_sites(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            def post(origin=None):
                headers = {"Content-Type": "application/json"} | ({"Origin": origin} if origin else {})
                r = urllib.request.Request(f"http://127.0.0.1:{port}/api/fetch", headers=headers,
                                           data=json.dumps({"url": "http://192.168.0.1/"}).encode())
                try:
                    with urllib.request.urlopen(r, timeout=30) as resp:
                        return resp.status, json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    return e.code, json.loads(e.read())
            code, body = post()
            self.assertEqual(code, 422)
            self.assertIn("home network", body["error"])
            self.assertEqual(post("https://evil.example")[0], 403)
        finally:
            srv.shutdown()
            srv.server_close()


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
            with urllib.request.urlopen(r, timeout=300) as resp:   # CI machines can be slow
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
        app_files = [
            "/", "/index.html",
            "/vendor/pdf.min.js", "/vendor/pdf.worker.min.js", "/vendor/mammoth.browser.min.js",
        ]
        for path in app_files:
            code, _, body = self.req(path)
            self.assertEqual(code, 200, path)
            self.assertGreater(len(body), 1000, path)

    def test_does_not_expose_other_files(self):
        private = ["/server.py", "/../server.py", "/models/voices-v1.0.bin", "/.venv/pyvenv.cfg", "/%2e%2e/server.py"]
        for path in private:
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
        for text in ["1,234.56 — $99 & 50% off!!! ???", "Café naïve résumé 😀", "A fairly long sentence, " * 6]:
            self.assertEqual(self.req("/api/kokoro", {"text": text})[0], 200, text[:30])

    def test_text_is_capped(self):
        captured = []
        real = server.synthesize
        server.synthesize = lambda text, voice, speed: captured.append(text) or b"RIFF"
        try:
            self.assertEqual(self.req("/api/kokoro", {"text": "word " * 400})[0], 200)
        finally:
            server.synthesize = real
        self.assertLessEqual(len(captured[0]), server.MAX_TEXT)


if __name__ == "__main__":
    unittest.main()
