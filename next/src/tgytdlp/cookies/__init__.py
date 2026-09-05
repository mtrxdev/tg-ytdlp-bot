from pathlib import Path

NETSCAPE_MARK = "# Netscape HTTP Cookie File"
MAX_COOKIE_BYTES = 100 * 1024
COOKIE_FILENAME = "cookie.txt"

TOO_LARGE = "That file is too big. Send a cookie.txt under 100 KB."
NOT_TEXT = "That file is not a text login file."
NOT_NETSCAPE = (
    "That file is not a YouTube login file. "
    "It must include the line “# Netscape HTTP Cookie File”."
)
NOT_TXT = "Send a .txt login file (paperclip → File), not a photo or video."


def user_cookie_path(data_dir: Path, chat_id: int) -> Path:
    return data_dir / "users" / str(chat_id) / COOKIE_FILENAME


def cookies_for_chat(data_dir: Path, chat_id: int) -> Path | None:
    path = user_cookie_path(data_dir, chat_id)
    if path.is_file():
        return path
    return None


def resolve_cookies(
    data_dir: Path,
    chat_id: int,
    fallback: Path | None,
) -> Path | None:
    user = cookies_for_chat(data_dir, chat_id)
    if user is not None:
        return user
    return fallback


def is_cookie_filename(name: str) -> bool:
    return Path(name).suffix.lower() == ".txt"


def validate_cookie_bytes(data: bytes) -> str | None:
    if len(data) > MAX_COOKIE_BYTES:
        return TOO_LARGE
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return NOT_TEXT
    if NETSCAPE_MARK not in text:
        return NOT_NETSCAPE
    return None


def save_user_cookies(data_dir: Path, chat_id: int, data: bytes) -> Path:
    error = validate_cookie_bytes(data)
    if error is not None:
        raise ValueError(error)
    dest = user_cookie_path(data_dir, chat_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return dest


def clear_user_cookies(data_dir: Path, chat_id: int) -> bool:
    path = user_cookie_path(data_dir, chat_id)
    if not path.is_file():
        return False
    path.unlink()
    return True
