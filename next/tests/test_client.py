import pytest

pytest.importorskip("pyrogram")

from tgytdlp.config import settings_from_mapping
from tgytdlp.telegram.client import build_client


def test_build_client_uses_session_name() -> None:
    settings = settings_from_mapping(
        {
            "TG_API_ID": "12345678",
            "TG_API_HASH": "0123456789abcdef",
            "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
            "TG_SESSION_NAME": "rewrite_probe",
        }
    )
    client = build_client(settings)
    assert client.name == "rewrite_probe"
    assert client.bot_token == settings.bot_token
