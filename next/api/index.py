from http.server import BaseHTTPRequestHandler

from tgytdlp.telegram.webhook import handle_http, header_name

_MAX_BODY = 1_000_000


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._send(200, b'{"ok":true,"service":"tgytdlp"}')

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length < 0 or length > _MAX_BODY:
            self._send(413, b'{"ok":false}')
            return
        raw = self.rfile.read(length)
        status, body = handle_http(raw, self.headers.get(header_name()))
        self._send(status, body)

    def do_HEAD(self) -> None:
        self._send(200, b"")

    def _send(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return None
