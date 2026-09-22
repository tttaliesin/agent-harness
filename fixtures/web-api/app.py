"""Small loopback-only HTTP fixture; public tokens are demonstration data."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path)
        if route.path == "/":
            self.respond(200, Path(__file__).with_name("index.html").read_bytes(), "text/html")
        elif route.path == "/health":
            self.json(200, {"service": "agent-harness-web-api", "ready": True})
        elif route.path == "/api/greet":
            name = parse_qs(route.query).get("name", [""])[0].strip()
            if not 1 <= len(name) <= 40:
                self.json(422, {"error": "Name must contain 1 to 40 characters"})
            else:
                self.json(200, {"message": f"Hello, {name}!"})
        elif route.path == "/api/admin":
            # Intentionally public, deterministic loopback fixture identities.
            token = self.headers.get("Authorization", "")
            if token == "Bearer public-fixture-admin":
                self.json(200, {"message": "Admin access granted"})
            elif token == "Bearer public-fixture-viewer":
                self.json(403, {"error": "Admin role required"})
            else:
                self.json(401, {"error": "Authentication required"})
        elif route.path == "/api/error":
            self.json(503, {"error": "Fixture service unavailable"})
        else:
            self.json(404, {"error": "Not found"})

    def json(self, status, payload):
        self.respond(status, json.dumps(payload).encode(), "application/json")

    def respond(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(json.dumps({"url": f"http://127.0.0.1:{server.server_port}"}), flush=True)
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
