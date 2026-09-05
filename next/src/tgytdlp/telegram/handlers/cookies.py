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
from tgytdlp.telegram.ids import is_private_chat
from tgytdlp.telegram.rich import cookies_rich, notice_rich
from tgytdlp.telegram.status import Status, send_status

COOKIES_HELP = (
    "On iPhone you cannot install Cookie-Editor. Safari and Chrome "
    "have no add-on for that. Export the .txt once on a computer, "
    "then send it here from your phone (paperclip → File).\n\n"
    "Then send the same YouTube link again.\n\n"
    "/clear_cookies removes the file I stored for this chat."
)
COOKIES_SAVED = (
    "Saved. Send the YouTube link again. "
    "I will use this login file only for this chat."
)
COOKIES_SAVED_PASTE = (
    "Saved. Send the YouTube link again. "
    "If your paste is still in this chat, delete that message."
)
COOKIES_CLEARED = "Removed the login file for this chat."
COOKIES_NONE = "I do not have a login file for this chat."
COOKIES_HAVE = "I already have a login file for this chat."
COOKIES_PRIVATE_ONLY = (
    "Send the login file in a private chat with me. "
    "Do not post cookies in a group."
)
SAVE_AS_HINT = (
    "In a private chat, send the .txt as a document (safer), "
    "or paste the cookie.txt text after the command.\n\n"
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


def _notice(
    api: BotAPI,
    chat_id: int,
    title: str,
    body: str,
    *,
    user_id: int | None = None,
    query_id: str | None = None,
    dismissable: bool = True,
) -> Status:
    return send_status(
        api,
        chat_id,
        notice_rich(title, body),
        user_id=user_id,
        query_id=query_id,
        dismissable=dismissable,
    )


def handle_cookies_help(
    api: BotAPI,
    data_dir: Path,
    chat_id: int,
    *,
    user_id: int | None = None,
    query_id: str | None = None,
) -> Status:
    return send_status(
        api,
        chat_id,
        cookies_rich(cookies_status_line(data_dir, chat_id), COOKIES_HELP),
        user_id=user_id,
        query_id=query_id,
        dismissable=True,
    )


def handle_clear_cookies(
    api: BotAPI,
    data_dir: Path,
    chat_id: int,
    *,
    user_id: int | None = None,
) -> Status:
    if clear_user_cookies(data_dir, chat_id):
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            COOKIES_CLEARED,
            user_id=user_id,
        )
    return _notice(
        api,
        chat_id,
        "YouTube sign-in file",
        COOKIES_NONE,
        user_id=user_id,
    )


def handle_save_as_cookie(
    api: BotAPI,
    data_dir: Path,
    chat_id: int,
    text: str,
    *,
    user_id: int | None = None,
    message_id: int | None = None,
) -> Status:
    if not is_private_chat(chat_id):
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            COOKIES_PRIVATE_ONLY,
            user_id=user_id,
        )
    parts = text.split(maxsplit=1)
    body = parts[1] if len(parts) > 1 else ""
    if not body.strip():
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            SAVE_AS_HINT,
            user_id=user_id,
        )
    try:
        data = body.encode("utf-8")
    except UnicodeEncodeError:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            "That text is not a login file.",
            user_id=user_id,
        )
    error = validate_cookie_bytes(data)
    if error is not None:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            error,
            user_id=user_id,
        )
    save_user_cookies(data_dir, chat_id, data)
    if message_id is not None:
        try:
            api.delete_message(chat_id, message_id)
        except BotAPIError:
            pass
    return _notice(
        api,
        chat_id,
        "YouTube sign-in file",
        COOKIES_SAVED_PASTE,
        user_id=user_id,
    )


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
    *,
    user_id: int | None = None,
) -> Status | None:
    name = str(document.get("file_name") or "")
    size = document.get("file_size")
    file_id = document.get("file_id")
    if not isinstance(file_id, str) or not file_id:
        return None
    if not is_private_chat(chat_id):
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            COOKIES_PRIVATE_ONLY,
            user_id=user_id,
        )
    if not is_cookie_filename(name):
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            NOT_TXT,
            user_id=user_id,
        )
    if isinstance(size, int) and size > MAX_COOKIE_BYTES:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            TOO_LARGE,
            user_id=user_id,
        )
    try:
        info = api.get_file(file_id)
    except BotAPIError:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            DOWNLOAD_FAILED,
            user_id=user_id,
        )
    file_path = info.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            DOWNLOAD_FAILED,
            user_id=user_id,
        )
    tmp = data_dir / "tmp" / f"{chat_id}-incoming-cookie.txt"
    try:
        api.download_file(file_path, tmp, max_bytes=MAX_COOKIE_BYTES)
        data = tmp.read_bytes()
    except (BotAPIError, OSError):
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            DOWNLOAD_FAILED,
            user_id=user_id,
        )
    finally:
        tmp.unlink(missing_ok=True)
        parent = tmp.parent
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
    error = validate_cookie_bytes(data)
    if error is not None:
        return _notice(
            api,
            chat_id,
            "YouTube sign-in file",
            error,
            user_id=user_id,
        )
    save_user_cookies(data_dir, chat_id, data)
    return _notice(
        api,
        chat_id,
        "YouTube sign-in file",
        COOKIES_SAVED,
        user_id=user_id,
    )
