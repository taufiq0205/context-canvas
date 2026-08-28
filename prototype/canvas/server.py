"""THROWAWAY Issue #6 prototype server. Never use in production."""

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if os.getenv("ENVIRONMENT") == "production" or os.getenv("NODE_ENV") == "production":
    raise SystemExit("Refusing to expose throwaway prototype in production")

ROOT = Path(__file__).parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print("THROWAWAY prototype: http://127.0.0.1:8000/?variant=A")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
