import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from server import WisecowHandler


class WisecowHandlerTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), WisecowHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_endpoint(self):
        from urllib.request import urlopen
        with urlopen(f"{self.base_url}/healthz") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"ok\n")

    def test_root_renders_escaped_fortune(self):
        from urllib.request import urlopen
        completed = type("Result", (), {"stdout": "<moo> & wisdom"})()
        with patch("server.subprocess.run", return_value=completed):
            with urlopen(f"{self.base_url}/") as response:
                body = response.read().decode("utf-8")
                self.assertEqual(response.status, 200)
                self.assertIn("&lt;moo&gt; &amp; wisdom", body)
                self.assertIn("Content-Security-Policy", response.headers)

    def test_unknown_path_returns_404(self):
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as error:
            from urllib.request import urlopen
            urlopen(f"{self.base_url}/missing")
        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
