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
