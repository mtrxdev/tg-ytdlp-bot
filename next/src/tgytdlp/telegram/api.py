from collections.abc import Mapping
from typing import IO

import requests

from tgytdlp.config import Settings


class BotAPIError(RuntimeError):
    def __init__(self, error_code: int, description: str) -> None:
        self.error_code = error_code
        self.description = description
        super().__init__(f"Bot API {error_code}: {description}")


def _as_object(value: object, what: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise BotAPIError(0, f"{what} was not an object")
    return {str(key): item for key, item in value.items()}


class BotAPI:
    def __init__(
        self,
        token: str,
        api_base: str,
        *,
        session: requests.Session | None = None,
        timeout: float = 70,
    ) -> None:
        if not token:
            raise BotAPIError(0, "bot token is empty")
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def method_url(self, method: str) -> str:
        return f"{self._api_base}/bot{self._token}/{method}"

    def call(
        self,
        method: str,
        payload: Mapping[str, object] | None = None,
        *,
        files: Mapping[str, tuple[str, IO[bytes]]] | None = None,
        timeout: float | None = None,
    ) -> object:
        http_timeout = self._timeout if timeout is None else timeout
        url = self.method_url(method)
        try:
            if files is not None:
                response = self._session.post(
                    url,
                    data=dict(payload or {}),
                    files=files,
                    timeout=http_timeout,
                )
            else:
                response = self._session.post(
                    url,
                    json=dict(payload or {}),
                    timeout=http_timeout,
                )
        except requests.RequestException as exc:
            raise BotAPIError(0, f"{method} request failed") from exc

        try:
            body: object = response.json()
        except ValueError as exc:
            raise BotAPIError(response.status_code, "response was not JSON") from exc

        parsed = _as_object(body, "response")
        if parsed.get("ok") is not True:
            code = parsed.get("error_code", response.status_code)
            description = parsed.get("description", "unknown error")
            raise BotAPIError(int(code) if isinstance(code, int) else 0, str(description))
        return parsed.get("result")

    def get_me(self) -> dict[str, object]:
        return _as_object(self.call("getMe"), "getMe")

    def get_updates(
        self,
        *,
        offset: int | None,
        timeout: int,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        payload: dict[str, object] = {"timeout": timeout, "limit": limit}
        if offset is not None:
            payload["offset"] = offset
        result = self.call("getUpdates", payload, timeout=float(timeout) + 10)
        if not isinstance(result, list):
            raise BotAPIError(0, "getUpdates did not return a list")
        updates: list[dict[str, object]] = []
        for item in result:
            updates.append(_as_object(item, "update"))
        return updates

    def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        reply_markup: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        payload: dict[str, object] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = dict(reply_markup)
        return _as_object(self.call("sendMessage", payload), "sendMessage")

    def answer_callback_query(
        self,
        callback_query_id: str,
        *,
        text: str | None = None,
    ) -> bool:
        payload: dict[str, object] = {"callback_query_id": callback_query_id}
        if text is not None:
            payload["text"] = text
        result = self.call("answerCallbackQuery", payload)
        return result is True

    def send_chat_action(self, chat_id: int, action: str) -> bool:
        result = self.call("sendChatAction", {"chat_id": chat_id, "action": action})
        return result is True

    def send_document(
        self,
        chat_id: int,
        path: str,
        *,
        use_file_uri: bool,
        filename: str | None = None,
    ) -> dict[str, object]:
        if use_file_uri:
            return _as_object(
                self.call(
                    "sendDocument",
                    {"chat_id": chat_id, "document": path},
                ),
                "sendDocument",
            )
        name = filename or path.rsplit("/", 1)[-1]
        with open(path, "rb") as handle:
            return _as_object(
                self.call(
                    "sendDocument",
                    {"chat_id": chat_id},
                    files={"document": (name, handle)},
                ),
                "sendDocument",
            )


def build_api(settings: Settings) -> BotAPI:
    return BotAPI(
        settings.bot_token,
        settings.api_base,
        timeout=float(settings.poll_timeout) + 15,
    )
