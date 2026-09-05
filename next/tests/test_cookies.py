from pathlib import Path

from tgytdlp.config import settings_from_mapping
from tgytdlp.cookies import (
    MAX_COOKIE_BYTES,
    NETSCAPE_MARK,
    NOT_NETSCAPE,
    NOT_TXT,
    TOO_LARGE,
    clear_user_cookies,
    cookies_for_chat,
    is_cookie_filename,
    resolve_cookies,
    save_user_cookies,
    user_cookie_path,
    validate_cookie_bytes,
)
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers import process_update
from tgytdlp.telegram.handlers.cookies import (
    COOKIES_CLEARED,
    COOKIES_HAVE,
    COOKIES_HELP,
    COOKIES_NONE,
    COOKIES_SAVED,
    is_clear_cookies_command,
    is_cookies_command,
    is_save_as_cookie_command,
)
from tests.support.botapi import FakeBotAPI

VALID = f"{NETSCAPE_MARK}\n.youtube.com\tTRUE\t/\tTRUE\t0\tSID\tx\n"


def _settings(tmp_path: Path, base: str) -> object:
    return settings_from_mapping(
        {
            "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
            "TG_API_BASE": base,
            "TG_DATA_DIR": str(tmp_path / "data"),
            "TG_POLL_TIMEOUT": "1",
        },
        relative_to=tmp_path,
    )


def test_cookie_filename_and_validate() -> None:
    assert is_cookie_filename("cookies.txt")
    assert is_cookie_filename("Cookie.TXT")
    assert not is_cookie_filename("clip.mp4")
    assert validate_cookie_bytes(VALID.encode()) is None
    assert validate_cookie_bytes(b"hello") == NOT_NETSCAPE
    assert validate_cookie_bytes(b"\xff\xfe") is not None
    assert validate_cookie_bytes(b"x" * (MAX_COOKIE_BYTES + 1)) == TOO_LARGE


def test_save_resolve_and_clear(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    fallback = tmp_path / "operator.txt"
    fallback.write_text(VALID, encoding="utf-8")
    assert cookies_for_chat(data_dir, 7) is None
    assert resolve_cookies(data_dir, 7, fallback) == fallback
    saved = save_user_cookies(data_dir, 7, VALID.encode())
    assert saved == user_cookie_path(data_dir, 7)
    assert saved.read_text(encoding="utf-8") == VALID
    assert resolve_cookies(data_dir, 7, fallback) == saved
    assert clear_user_cookies(data_dir, 7) is True
    assert cookies_for_chat(data_dir, 7) is None
    assert clear_user_cookies(data_dir, 7) is False


def test_cookie_commands() -> None:
    assert is_cookies_command("/cookies")
    assert is_cookies_command("/cookies@mtrxdevbot")
    assert is_clear_cookies_command("/clear_cookies")
    assert is_save_as_cookie_command("/save_as_cookie")
    assert not is_cookies_command("/start")


def test_process_update_save_as_cookie_and_clear(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = _settings(tmp_path, fake.base_url)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        process_update(
            api,
            settings,
            store,
            {"message": {"chat": {"id": 11}, "text": "/cookies"}},
        )
        help_body = fake.calls[-1]["body"]
        assert isinstance(help_body, dict)
        assert COOKIES_NONE in str(help_body["text"])
        assert COOKIES_HELP in str(help_body["text"])
        process_update(
            api,
            settings,
            store,
            {
                "message": {
                    "chat": {"id": 11},
                    "text": f"/save_as_cookie\n{VALID}",
                }
            },
        )
        assert cookies_for_chat(settings.data_dir, 11) is not None
        saved_body = fake.calls[-1]["body"]
        assert isinstance(saved_body, dict)
        assert saved_body["text"] == COOKIES_SAVED
        process_update(
            api,
            settings,
            store,
            {"message": {"chat": {"id": 11}, "text": "/cookies"}},
        )
        have_body = fake.calls[-1]["body"]
        assert isinstance(have_body, dict)
        assert COOKIES_HAVE in str(have_body["text"])
        process_update(
            api,
            settings,
            store,
            {"message": {"chat": {"id": 11}, "text": "/clear_cookies"}},
        )
        clear_body = fake.calls[-1]["body"]
        assert isinstance(clear_body, dict)
        assert clear_body["text"] == COOKIES_CLEARED
        store.close()
    finally:
        fake.stop()


def test_process_update_cookie_document(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.add_document("fileAAA", VALID.encode())
    fake.start()
    try:
        settings = _settings(tmp_path, fake.base_url)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        process_update(
            api,
            settings,
            store,
            {
                "message": {
                    "chat": {"id": 22},
                    "document": {
                        "file_id": "fileAAA",
                        "file_name": "cookies.txt",
                        "file_size": len(VALID.encode()),
                    },
                }
            },
        )
        path = cookies_for_chat(settings.data_dir, 22)
        assert path is not None
        assert path.read_text(encoding="utf-8") == VALID
        methods = [str(call["method"]) for call in fake.calls]
        assert "getFile" in methods
        body = fake.calls[-1]["body"]
        assert isinstance(body, dict)
        assert body["text"] == COOKIES_SAVED
        store.close()
    finally:
        fake.stop()


def test_process_update_rejects_non_txt_document(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = _settings(tmp_path, fake.base_url)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        process_update(
            api,
            settings,
            store,
            {
                "message": {
                    "chat": {"id": 22},
                    "document": {
                        "file_id": "fileBBB",
                        "file_name": "clip.mp4",
                        "file_size": 12,
                    },
                }
            },
        )
        body = fake.calls[-1]["body"]
        assert isinstance(body, dict)
        assert body["text"] == NOT_TXT
        assert cookies_for_chat(settings.data_dir, 22) is None
        store.close()
    finally:
        fake.stop()
