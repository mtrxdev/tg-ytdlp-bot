from tgytdlp.config import settings_from_mapping
from tgytdlp.telegram.client import build_client


def test_build_client_uses_token_and_base() -> None:
    settings = settings_from_mapping(
        {
            "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
            "TG_API_BASE": "http://127.0.0.1:8081",
        }
    )
    client = build_client(settings)
    assert client.method_url("getMe").startswith("http://127.0.0.1:8081/bot")
    assert client.method_url("getMe").endswith("/getMe")
