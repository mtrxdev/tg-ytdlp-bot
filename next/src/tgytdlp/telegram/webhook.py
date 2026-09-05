import hashlib
import hmac
import json
import logging
import os
import re
from collections.abc import Mapping

from tgytdlp.config import Settings, SettingsError, settings_from_mapping
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI, build_api
from tgytdlp.telegram.handlers import process_update

logger = logging.getLogger(__name__)

_SECRET_RE = re.compile(r"^[A-Za-z0-9_-]{1,256}$")
_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"
_DERIVE_KEY = b"tgytdlp-webhook-v1"


def apply_vercel_defaults(env: dict[str, str]) -> None:
    if env.get("VERCEL") != "1":
        return
    env.setdefault("TG_DATA_DIR", "/tmp/tgytdlp")
    env.setdefault("TG_WORKER_TIMEOUT", "240")


def webhook_secret(settings: Settings, env: Mapping[str, str] | None = None) -> str:
    environ = os.environ if env is None else env
    override = str(environ.get("TG_WEBHOOK_SECRET", "")).strip()
    if override:
        if not _SECRET_RE.match(override):
            raise SettingsError("TG_WEBHOOK_SECRET must be 1-256 A-Z a-z 0-9 _ -")
        return override
    digest = hmac.new(_DERIVE_KEY, settings.bot_token.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()


def secrets_match(header: str | None, expected: str) -> bool:
    got = header if isinstance(header, str) else ""
    if not expected:
        return False
    if len(got) != len(expected):
        return False
    return hmac.compare_digest(got, expected)


def parse_update(raw: bytes) -> dict[str, object] | None:
    try:
        data: object = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return {str(key): value for key, value in data.items()}


def apply_update(
    api: BotAPI,
    settings: Settings,
    store: Store,
    update: Mapping[str, object],
) -> bool:
    raw_id = update.get("update_id")
    if isinstance(raw_id, int) and not store.claim_update(raw_id):
        return False
    process_update(api, settings, store, update)
    return True


def handle_http(
    raw: bytes,
    secret_header: str | None,
    *,
    env: Mapping[str, str] | None = None,
) -> tuple[int, bytes]:
    environ = dict(os.environ if env is None else env)
    apply_vercel_defaults(environ)
    try:
        settings = settings_from_mapping(environ)
        expected = webhook_secret(settings, environ)
    except SettingsError:
        return 500, b'{"ok":false}'
    if not secrets_match(secret_header, expected):
        return 401, b'{"ok":false}'
    update = parse_update(raw)
    if update is None:
        return 400, b'{"ok":false}'
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    store = Store(settings.data_dir / "bot.sqlite")
    try:
        apply_update(build_api(settings), settings, store, update)
    except Exception:
        logger.error("webhook update failed")
        return 500, b'{"ok":false}'
    finally:
        store.close()
    return 200, b'{"ok":true}'


def header_name() -> str:
    return _SECRET_HEADER
