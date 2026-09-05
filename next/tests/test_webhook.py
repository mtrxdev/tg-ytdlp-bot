from pathlib import Path

from tgytdlp.config import settings_from_mapping
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.webhook import (
    apply_update,
    apply_vercel_defaults,
    handle_http,
    parse_update,
    secrets_match,
    webhook_secret,
)
from tests.support.botapi import FakeBotAPI


def _env(tmp_path: Path, base: str, **extra: str) -> dict[str, str]:
    values = {
        "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
        "TG_API_BASE": base,
        "TG_DATA_DIR": str(tmp_path / "data"),
        "TG_POLL_TIMEOUT": "1",
    }
    values.update(extra)
    return values


def test_parse_update_rejects_garbage() -> None:
    assert parse_update(b"") is None
    assert parse_update(b"[]") is None
    assert parse_update(b'{"update_id": 1}') == {"update_id": 1}


def test_webhook_secret_is_not_the_bot_token() -> None:
    settings = settings_from_mapping(
        {"TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx"}
    )
    secret = webhook_secret(settings, {})
    assert ":" not in secret
    assert settings.bot_token not in secret
    assert secrets_match(secret, secret) is True
    assert secrets_match("nope", secret) is False


def test_vercel_defaults_only_when_flagged() -> None:
    plain: dict[str, str] = {}
    apply_vercel_defaults(plain)
    assert "TG_DATA_DIR" not in plain
    vercel = {"VERCEL": "1"}
    apply_vercel_defaults(vercel)
    assert vercel["TG_DATA_DIR"] == "/tmp/tgytdlp"
    assert vercel["TG_WORKER_TIMEOUT"] == "240"


def test_handle_http_rejects_bad_secret(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        status, body = handle_http(
            b'{"update_id": 1, "message": {"chat": {"id": 3}, "text": "/start"}}',
            "wrong",
            env=_env(tmp_path, fake.base_url),
        )
    finally:
        fake.stop()
    assert status == 401
    assert body == b'{"ok":false}'
    assert fake.calls == []


def test_handle_http_start_and_dedupes(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        env = _env(tmp_path, fake.base_url)
        settings = settings_from_mapping(env, relative_to=tmp_path)
        secret = webhook_secret(settings, env)
        payload = b'{"update_id": 9, "message": {"chat": {"id": 3}, "text": "/start"}}'
        first = handle_http(payload, secret, env=env)
        second = handle_http(payload, secret, env=env)
    finally:
        fake.stop()
    assert first == (200, b'{"ok":true}')
    assert second == (200, b'{"ok":true}')
    methods = [str(call["method"]) for call in fake.calls]
    assert methods.count("sendRichMessage") == 1


def test_claim_update_skips_second_apply(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = settings_from_mapping(_env(tmp_path, fake.base_url), relative_to=tmp_path)
        settings.data_dir.mkdir(parents=True)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        update = {"update_id": 4, "message": {"chat": {"id": 3}, "text": "/start"}}
        assert apply_update(api, settings, store, update) is True
        assert apply_update(api, settings, store, update) is False
        store.close()
    finally:
        fake.stop()
    methods = [str(call["method"]) for call in fake.calls]
    assert methods.count("sendRichMessage") == 1
