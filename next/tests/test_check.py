from tgytdlp.__main__ import main
from tests.support.botapi import FakeBotAPI


def test_check_prints_username(capsys: object, monkeypatch: object) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        monkeypatch.setenv("TG_BOT_TOKEN", fake.token)
        monkeypatch.setenv("TG_API_BASE", fake.base_url)
        code = main(["--check"])
        captured = capsys.readouterr()
    finally:
        fake.stop()
    assert code == 0
    assert captured.out.strip() == "@mtrxdevbot"


def test_set_webhook_prints_ok(capsys: object, monkeypatch: object) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        monkeypatch.setenv("TG_BOT_TOKEN", fake.token)
        monkeypatch.setenv("TG_API_BASE", fake.base_url)
        code = main(["--set-webhook", "https://example.vercel.app/api/telegram"])
        captured = capsys.readouterr()
    finally:
        fake.stop()
    assert code == 0
    assert captured.out.strip().splitlines()[-1] == "webhook set"
    webhook = next(call for call in fake.calls if call["method"] == "setWebhook")
    body = webhook["body"]
    assert isinstance(body, dict)
    assert body["url"] == "https://example.vercel.app/api/telegram"
    assert isinstance(body["secret_token"], str)
    assert fake.token not in str(body["secret_token"])


def test_delete_webhook_prints_ok(capsys: object, monkeypatch: object) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        monkeypatch.setenv("TG_BOT_TOKEN", fake.token)
        monkeypatch.setenv("TG_API_BASE", fake.base_url)
        code = main(["--delete-webhook"])
        captured = capsys.readouterr()
    finally:
        fake.stop()
    assert code == 0
    assert captured.out.strip().splitlines()[-1] == "webhook deleted"
    assert any(call["method"] == "deleteWebhook" for call in fake.calls)
