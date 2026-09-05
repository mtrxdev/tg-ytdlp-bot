from collections.abc import Mapping
from pathlib import Path

from tgytdlp.cookies import (
    MAX_COOKIE_BYTES,
    NOT_TXT,
    TOO_LARGE,
    clear_user_cookies,
    cookies_for_chat,
    is_cookie_filename,
    save_user_cookies,
    validate_cookie_bytes,
)
from tgytdlp.telegram.api import BotAPI, BotAPIError

COOKIES_HELP = (
    "Some YouTube videos need you to be signed in. You do this once "
    "inside Telegram — no settings files.\n\n"
    "1. On your phone or computer, open YouTube in the browser where "
    "you are already signed in.\n"
    "2. Install Cookie-Editor or “Get cookies.txt LOCALLY”.\n"
    "3. Export cookies as a .txt file.\n"
    "4. Send that file here as a document (paperclip → File). "
    "Not a screenshot.\n\n"
    "Then send the same YouTube link again.\n\n"
    "/clear_cookies removes the file I stored for this chat."
)
COOKIES_SAVED = (
    "Saved. Send the YouTube link again. "
    "I will use this login file only for this chat."
)
COOKIES_CLEARED = "Removed the login file for this chat."
COOKIES_NONE = "I do not have a login file for this chat."
COOKIES_HAVE = "I already have a login file for this chat."
SAVE_AS_HINT = (
    "Paste the cookie.txt text after the command, or send the .txt "
    "as a document.\n\n"
    "/save_as_cookie\n"
    "# Netscape HTTP Cookie File\n"
    "…"
)
DOWNLOAD_FAILED = "I could not read that file. Try sending the .txt again."


def _command_name(text: str) -> str:
    first = text.split(maxsplit=1)[0]
    return first.split("@", 1)[0]


def is_cookies_command(text: str) -> bool:
    return _command_name(text) == "/cookies"


def is_clear_cookies_command(text: str) -> bool:
    return _command_name(text) == "/clear_cookies"


def is_save_as_cookie_command(text: str) -> bool:
    return _command_name(text) == "/save_as_cookie"


def cookies_status_line(data_dir: Path, chat_id: int) -> str:
    if cookies_for_chat(data_dir, chat_id) is None:
        return COOKIES_NONE
    return COOKIES_HAVE


def handle_cookies_help(api: BotAPI, data_dir: Path, chat_id: int) -> dict[str, object]:
    text = f"{cookies_status_line(data_dir, chat_id)}\n\n{COOKIES_HELP}"
    return api.send_message(chat_id, text)


def handle_clear_cookies(api: BotAPI, data_dir: Path, chat_id: int) -> dict[str, object]:
    if clear_user_cookies(data_dir, chat_id):
        return api.send_message(chat_id, COOKIES_CLEARED)
    return api.send_message(chat_id, COOKIES_NONE)


def handle_save_as_cookie(
    api: BotAPI,
    data_dir: Path,
    chat_id: int,
    text: str,
) -> dict[str, object]:
    parts = text.split(maxsplit=1)
    body = parts[1] if len(parts) > 1 else ""
    if not body.strip():
        return api.send_message(chat_id, SAVE_AS_HINT)
    try:
        data = body.encode("utf-8")
    except UnicodeEncodeError:
        return api.send_message(chat_id, "That text is not a login file.")
    error = validate_cookie_bytes(data)
    if error is not None:
        return api.send_message(chat_id, error)
    save_user_cookies(data_dir, chat_id, data)
    return api.send_message(chat_id, COOKIES_SAVED)


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {str(key): item for key, item in value.items()}


def document_from_message(message: Mapping[str, object]) -> Mapping[str, object] | None:
    return _as_mapping(message.get("document"))


def handle_cookie_document(
    api: BotAPI,
    data_dir: Path,
    chat_id: int,
    document: Mapping[str, object],
) -> dict[str, object] | None:
    name = str(document.get("file_name") or "")
    size = document.get("file_size")
    file_id = document.get("file_id")
    if not isinstance(file_id, str) or not file_id:
        return None
    if not is_cookie_filename(name):
        return api.send_message(chat_id, NOT_TXT)
    if isinstance(size, int) and size > MAX_COOKIE_BYTES:
        return api.send_message(chat_id, TOO_LARGE)
    try:
        info = api.get_file(file_id)
    except BotAPIError:
        return api.send_message(chat_id, DOWNLOAD_FAILED)
    file_path = info.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return api.send_message(chat_id, DOWNLOAD_FAILED)
    tmp = data_dir / "tmp" / f"{chat_id}-incoming-cookie.txt"
    try:
        api.download_file(file_path, tmp, max_bytes=MAX_COOKIE_BYTES)
        data = tmp.read_bytes()
    except (BotAPIError, OSError):
        return api.send_message(chat_id, DOWNLOAD_FAILED)
    finally:
        tmp.unlink(missing_ok=True)
        parent = tmp.parent
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
    error = validate_cookie_bytes(data)
    if error is not None:
        return api.send_message(chat_id, error)
    save_user_cookies(data_dir, chat_id, data)
    return api.send_message(chat_id, COOKIES_SAVED)
