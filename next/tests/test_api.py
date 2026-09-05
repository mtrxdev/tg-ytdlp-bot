from pathlib import Path

import pytest

from tgytdlp.telegram.api import BotAPI, BotAPIError
from tests.support.botapi import FakeBotAPI


@pytest.fixture
def fake() -> FakeBotAPI:
    server = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    server.start()
    yield server
    server.stop()


def test_get_me(fake: FakeBotAPI) -> None:
    api = BotAPI(fake.token, fake.base_url)
    me = api.get_me()
    assert me["username"] == "mtrxdevbot"
    assert fake.calls[0]["method"] == "getMe"


def test_get_updates_and_send_message(fake: FakeBotAPI) -> None:
    fake.push_update(
        {
            "update_id": 7,
            "message": {"chat": {"id": 42}, "text": "/start"},
        }
    )
    api = BotAPI(fake.token, fake.base_url)
    updates = api.get_updates(offset=None, timeout=1)
    assert updates[0]["update_id"] == 7
    api.send_message(42, "hello", reply_markup={"inline_keyboard": [[{"text": "A", "callback_data": "a"}]]})
    send = fake.calls[-1]
    assert send["method"] == "sendMessage"
    body = send["body"]
    assert isinstance(body, dict)
    assert body["text"] == "hello"
    markup = body["reply_markup"]
    assert isinstance(markup, dict)
    assert "inline_keyboard" in markup


def test_send_document_file_uri_and_multipart(fake: FakeBotAPI, tmp_path: Path) -> None:
    api = BotAPI(fake.token, fake.base_url)
    sample = tmp_path / "clip.txt"
    sample.write_text("hi\n", encoding="utf-8")
    api.send_document(9, sample.as_uri(), use_file_uri=True, filename="clip.txt")
    uri_call = fake.calls[-1]
    assert uri_call["method"] == "sendDocument"
    body = uri_call["body"]
    assert isinstance(body, dict)
    assert str(body["document"]).startswith("file:")
    api.send_document(9, str(sample), use_file_uri=False, filename="clip.txt")
    multi = fake.calls[-1]
    assert "multipart" in str(multi["content_type"])


def test_get_file_and_download(fake: FakeBotAPI, tmp_path: Path) -> None:
    payload = b"# Netscape HTTP Cookie File\n"
    fake.add_document("fileCCC", payload)
    api = BotAPI(fake.token, fake.base_url)
    info = api.get_file("fileCCC")
    dest = tmp_path / "got.txt"
    api.download_file(str(info["file_path"]), dest, max_bytes=1024)
    assert dest.read_bytes() == payload


def test_error_payload(fake: FakeBotAPI) -> None:
    fake.override("getMe", {"ok": False, "error_code": 401, "description": "Unauthorized"})
    api = BotAPI(fake.token, fake.base_url)
    with pytest.raises(BotAPIError, match="401"):
        api.get_me()
