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
        self._file_ids: dict[str, str] = {}
        self._file_bytes: dict[str, bytes] = {}
        self._next_message_id = 1
        owner = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "FakeBotAPI/1.0"
            fake: ClassVar[FakeBotAPI]

            def log_message(self, _format: str, *_args: object) -> None:
                return None

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) >= 3 and parts[0] == "file" and parts[1].startswith("bot"):
                    file_path = "/".join(parts[2:])
                    data = owner._file_bytes.get(file_path)
                    if data is None:
                        self.send_response(404)
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

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
                elif method == "getFile":
                    file_id = ""
                    if isinstance(body, dict):
                        raw_id = body.get("file_id")
                        file_id = raw_id if isinstance(raw_id, str) else ""
                    stored = owner._file_ids.get(file_id)
                    if stored is None:
                        payload = {
                            "ok": False,
                            "error_code": 400,
                            "description": "file not found",
                        }
                    else:
                        payload = {
                            "ok": True,
                            "result": {
                                "file_id": file_id,
                                "file_path": stored,
                                "file_size": len(owner._file_bytes.get(stored, b"")),
                            },
                        }
                elif method in {
                    "sendMessage",
                    "sendRichMessage",
                    "sendDocument",
                }:
                    mid = owner._next_message_id
                    owner._next_message_id += 1
                    payload = {"ok": True, "result": {"message_id": mid}}
                elif method in {
                    "answerCallbackQuery",
                    "sendChatAction",
                    "editMessageText",
                    "editEphemeralMessageText",
                    "deleteMessage",
                    "deleteMessages",
                    "deleteEphemeralMessage",
                    "setMessageReaction",
                    "sendRichMessageDraft",
                    "setWebhook",
                    "deleteWebhook",
                }:
                    payload = {"ok": True, "result": True}
                elif method == "getWebhookInfo":
                    payload = {
                        "ok": True,
                        "result": {
                            "url": "",
                            "has_custom_certificate": False,
                            "pending_update_count": 0,
                        },
                    }
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

    def add_document(
        self,
        file_id: str,
        content: bytes,
        *,
        file_path: str | None = None,
    ) -> str:
        path = file_path or f"documents/{file_id}.txt"
        self._file_ids[file_id] = path
        self._file_bytes[path] = content
        return path
