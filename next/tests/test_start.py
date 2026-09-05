from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers.start import START_TEXT, handle_start, is_start_command, start_keyboard
from tests.support.botapi import FakeBotAPI


def test_start_command_names() -> None:
    assert is_start_command("/start")
    assert is_start_command("/start@mtrxdevbot")
    assert not is_start_command("/help")


def test_start_keyboard_is_inline() -> None:
    markup = start_keyboard()
    rows = markup["inline_keyboard"]
    assert isinstance(rows, list)
    assert rows[0][0]["callback_data"] == "how"
    assert rows[1][0]["callback_data"] == "cookies"
    assert rows[2][0]["callback_data"] == "sample"


def test_handle_start_sends_keyboard() -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        api = BotAPI(fake.token, fake.base_url)
        handle_start(api, 99)
    finally:
        fake.stop()
    send = fake.calls[-1]
    assert send["method"] == "sendMessage"
    body = send["body"]
    assert isinstance(body, dict)
    assert body["text"] == START_TEXT
    markup = body["reply_markup"]
    assert isinstance(markup, dict)
    assert "inline_keyboard" in markup
