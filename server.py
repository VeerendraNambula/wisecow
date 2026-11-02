#!/usr/bin/env python3
"""Small HTTP service that serves a random fortune rendered by cowsay."""

import html
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class WisecowHandler(BaseHTTPRequestHandler):
    server_version = "Wisecow/1.0"

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(200, "text/plain; charset=utf-8", b"ok\n")
            return
        if self.path != "/":
            self._send(404, "text/plain; charset=utf-8", b"Not found\n")
            return

        try:
            fortune = subprocess.run(
                ["fortune"], check=True, capture_output=True, text=True, timeout=3
            ).stdout.strip()
            cow = subprocess.run(
                ["cowsay", fortune], check=True, capture_output=True, text=True, timeout=3
            ).stdout
        except (OSError, subprocess.SubprocessError) as error:
            self.log_error("fortune/cowsay failed: %s", error)
            self._send(503, "text/plain; charset=utf-8", b"Wisdom service temporarily unavailable\n")
            return

        escaped = html.escape(cow)
        page = (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Wisecow</title><style>"
            "body{margin:0;min-height:100vh;display:grid;place-items:center;"
            "background:#101827;color:#e5e7eb;font:16px system-ui,sans-serif}"
            "main{max-width:900px;padding:2rem}h1{color:#a7f3d0}"
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.45 monospace}"
            "a{color:#93c5fd}</style></head><body><main>"
            "<h1>🐄 A little wisdom for your day</h1>"
            f"<pre>{escaped}</pre><p><a href='/'>Another fortune</a></p>"
            "</main></body></html>"
        )
        self._send(200, "text/html; charset=utf-8", page.encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        # Keep standard request logging, but avoid exposing request headers or secrets.
        super().log_message(format, *args)


def main() -> None:
    port = int(os.getenv("PORT", "4499"))
    server = ThreadingHTTPServer(("0.0.0.0", port), WisecowHandler)
    server.daemon_threads = True
    print(f"Wisecow listening on 0.0.0.0:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Wisecow", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
