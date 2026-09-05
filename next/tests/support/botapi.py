import json
import threading
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar
from urllib.parse import urlparse


class FakeBotAPI:
    def __init__(self, token: str) -> None:
        self.token = token
        self.calls: list[dict[str, object]] = []
        self._updates: list[dict[str, object]] = []
        self._overrides: dict[str, object] = {}
        owner = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "FakeBotAPI/1.0"
            fake: ClassVar[FakeBotAPI]

            def log_message(self, _format: str, *_args: object) -> None:
                return None

            def do_POST(self) -> None:
                parsed = urlparse(self.path)
                parts = parsed.path.strip("/").split("/")
                token = ""
                method = ""
                if len(parts) >= 2 and parts[0].startswith("bot"):
                    token = parts[0][3:]
                    method = parts[1]
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length)
                content_type = self.headers.get("Content-Type", "")
                body: object
                if "application/json" in content_type:
                    body = json.loads(raw.decode("utf-8") or "{}")
                else:
                    body = raw.decode("utf-8", errors="replace")
                owner.calls.append(
                    {
                        "method": method,
                        "token": token,
                        "content_type": content_type,
                        "body": body,
                    }
                )
                if method in owner._overrides:
                    payload = owner._overrides[method]
                elif method == "getUpdates":
                    updates = list(owner._updates)
                    owner._updates.clear()
                    payload = {"ok": True, "result": updates}
                elif method == "getMe":
                    payload = {
                        "ok": True,
                        "result": {
                            "id": 1,
                            "is_bot": True,
                            "first_name": "mtrxdevbot",
                            "username": "mtrxdevbot",
                        },
                    }
                elif method in {
                    "sendMessage",
                    "sendDocument",
                    "answerCallbackQuery",
                    "sendChatAction",
                }:
                    payload = {"ok": True, "result": True if method != "sendMessage" and method != "sendDocument" else {"message_id": 1}}
                else:
                    payload = {"ok": False, "error_code": 404, "description": f"unknown {method}"}
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        Handler.fake = self
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)

    def push_update(self, update: Mapping[str, object]) -> None:
        self._updates.append(dict(update))

    def override(self, method: str, payload: Mapping[str, object]) -> None:
        self._overrides[method] = dict(payload)
