from collections.abc import Mapping
from pathlib import Path
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
        reply_parameters: Mapping[str, object] | None = None,
        link_preview_options: Mapping[str, object] | None = None,
        ephemeral_message_parameters: Mapping[str, object] | None = None,
        parse_mode: str | None = None,
    ) -> dict[str, object]:
        payload: dict[str, object] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = dict(reply_markup)
        if reply_parameters is not None:
            payload["reply_parameters"] = dict(reply_parameters)
        if link_preview_options is not None:
            payload["link_preview_options"] = dict(link_preview_options)
        if ephemeral_message_parameters is not None:
            payload["ephemeral_message_parameters"] = dict(ephemeral_message_parameters)
        if parse_mode is not None:
            payload["parse_mode"] = parse_mode
        return _as_object(self.call("sendMessage", payload), "sendMessage")

    def send_rich_message(
        self,
        chat_id: int,
        rich_message: Mapping[str, object],
        *,
        reply_markup: Mapping[str, object] | None = None,
        reply_parameters: Mapping[str, object] | None = None,
        ephemeral_message_parameters: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "chat_id": chat_id,
            "rich_message": dict(rich_message),
        }
        if reply_markup is not None:
            payload["reply_markup"] = dict(reply_markup)
        if reply_parameters is not None:
            payload["reply_parameters"] = dict(reply_parameters)
        if ephemeral_message_parameters is not None:
            payload["ephemeral_message_parameters"] = dict(ephemeral_message_parameters)
        return _as_object(self.call("sendRichMessage", payload), "sendRichMessage")

    def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        *,
        text: str | None = None,
        rich_message: Mapping[str, object] | None = None,
        reply_markup: Mapping[str, object] | None = None,
    ) -> dict[str, object] | bool:
        payload: dict[str, object] = {"chat_id": chat_id, "message_id": message_id}
        if text is not None:
            payload["text"] = text
        if rich_message is not None:
            payload["rich_message"] = dict(rich_message)
        if reply_markup is not None:
            payload["reply_markup"] = dict(reply_markup)
        result = self.call("editMessageText", payload)
        if result is True:
            return True
        return _as_object(result, "editMessageText")

    def edit_ephemeral_message_text(
        self,
        chat_id: int,
        receiver_user_id: int,
        ephemeral_message_id: int,
        *,
        text: str | None = None,
        rich_message: Mapping[str, object] | None = None,
        reply_markup: Mapping[str, object] | None = None,
    ) -> bool:
        payload: dict[str, object] = {
            "chat_id": chat_id,
            "receiver_user_id": receiver_user_id,
            "ephemeral_message_id": ephemeral_message_id,
        }
        if text is not None:
            payload["text"] = text
        if rich_message is not None:
            payload["rich_message"] = dict(rich_message)
        if reply_markup is not None:
            payload["reply_markup"] = dict(reply_markup)
        return self.call("editEphemeralMessageText", payload) is True

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        return (
            self.call(
                "deleteMessage",
                {"chat_id": chat_id, "message_id": message_id},
            )
            is True
        )

    def delete_messages(self, chat_id: int, message_ids: list[int]) -> bool:
        return (
            self.call(
                "deleteMessages",
                {"chat_id": chat_id, "message_ids": list(message_ids)},
            )
            is True
        )

    def delete_ephemeral_message(
        self,
        chat_id: int,
        receiver_user_id: int,
        ephemeral_message_id: int,
    ) -> bool:
        return (
            self.call(
                "deleteEphemeralMessage",
                {
                    "chat_id": chat_id,
                    "receiver_user_id": receiver_user_id,
                    "ephemeral_message_id": ephemeral_message_id,
                },
            )
            is True
        )

    def set_message_reaction(
        self,
        chat_id: int,
        message_id: int,
        emoji: str,
        *,
        is_big: bool = False,
    ) -> bool:
        return (
            self.call(
                "setMessageReaction",
                {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "reaction": [{"type": "emoji", "emoji": emoji}],
                    "is_big": is_big,
                },
            )
            is True
        )

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

    def get_file(self, file_id: str) -> dict[str, object]:
        return _as_object(self.call("getFile", {"file_id": file_id}), "getFile")

    def download_file(self, file_path: str, dest: Path, *, max_bytes: int) -> None:
        parts = [part for part in file_path.split("/") if part]
        if not parts or ".." in parts:
            raise BotAPIError(0, "getFile path is invalid")
        safe_path = "/".join(parts)
        url = f"{self._api_base}/file/bot{self._token}/{safe_path}"
        try:
            response = self._session.get(url, timeout=self._timeout, stream=True)
        except requests.RequestException as exc:
            raise BotAPIError(0, "getFile download failed") from exc
        if response.status_code != 200:
            response.close()
            raise BotAPIError(response.status_code, "getFile download failed")
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".tmp")
        written = 0
        try:
            with tmp.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > max_bytes:
                        raise BotAPIError(0, "file is too large")
                    handle.write(chunk)
            tmp.replace(dest)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
        finally:
            response.close()

    def send_document(
        self,
        chat_id: int,
        path: str,
        *,
        use_file_uri: bool,
        filename: str | None = None,
        reply_parameters: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        extra: dict[str, object] = {"chat_id": chat_id}
        if reply_parameters is not None:
            extra["reply_parameters"] = dict(reply_parameters)
        if use_file_uri:
            extra["document"] = path
            return _as_object(self.call("sendDocument", extra), "sendDocument")
        name = filename or path.rsplit("/", 1)[-1]
        with open(path, "rb") as handle:
            return _as_object(
                self.call(
                    "sendDocument",
                    extra,
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
