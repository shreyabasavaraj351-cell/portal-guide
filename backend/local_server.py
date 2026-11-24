"""Run the backend locally for the demo: python backend/local_server.py
Same logic as the Lambda. Works offline using the built-in glossary.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import core


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, b'{"error":"bad json"}')
        result = core.explain(payload)
        if payload.get("speak"):
            result["audio_b64"] = core.tts(result["explanation"], payload.get("lang", "en"))
        self._send(200, json.dumps(result, ensure_ascii=False).encode())


if __name__ == "__main__":
    print("Backend on http://localhost:8787/explain")
    HTTPServer(("localhost", 8787), Handler).serve_forever()
