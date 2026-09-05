from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{20,}$")
_ENV_KEYS = {
    "api_id": "TG_API_ID",
    "api_hash": "TG_API_HASH",
    "bot_token": "TG_BOT_TOKEN",
    "session_name": "TG_SESSION_NAME",
}


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    session_name: str
    source_path: Path | None


def _next_root() -> Path:
    return Path(__file__).resolve().parents[3]


def config_candidates() -> tuple[Path, ...]:
    override = os.environ.get("TG_YTDLP_CONFIG")
    if override:
        return (Path(override),)
    return (Path.cwd() / "settings.toml", _next_root() / "settings.toml")


def _first_config_file() -> Path | None:
    for path in config_candidates():
        if path.is_file():
            return path
    return None


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise SettingsError("settings.toml must be a table")
    return data


def settings_from_mapping(
    env: Mapping[str, str],
    *,
    source_path: Path | None = None,
) -> Settings:
    return settings_from_values(
        api_id=env.get("TG_API_ID", ""),
        api_hash=env.get("TG_API_HASH", ""),
        bot_token=env.get("TG_BOT_TOKEN", ""),
        session_name=env.get("TG_SESSION_NAME", ""),
        source_path=source_path,
    )


def settings_from_values(
    *,
    api_id: object,
    api_hash: object,
    bot_token: object,
    session_name: object,
    source_path: Path | None = None,
) -> Settings:
    raw_id = str(api_id).strip()
    hash_text = str(api_hash).strip()
    token_text = str(bot_token).strip()
    session_text = str(session_name).strip() or "tgytdlp"

    if not raw_id.lstrip("-").isdigit():
        raise SettingsError("api_id must be a positive integer")
    parsed_id = int(raw_id)
    if parsed_id <= 0:
        raise SettingsError("api_id must be a positive integer")
    if len(hash_text) < 8:
        raise SettingsError("api_hash is missing or too short")
    if not _TOKEN_RE.match(token_text):
        raise SettingsError("bot_token is not a bot token")

    return Settings(
        api_id=parsed_id,
        api_hash=hash_text,
        bot_token=token_text,
        session_name=session_text,
        source_path=source_path,
    )


def _merge(toml_data: Mapping[str, Any], env: Mapping[str, str]) -> dict[str, object]:
    merged: dict[str, object] = {
        "api_id": toml_data.get("api_id", ""),
        "api_hash": toml_data.get("api_hash", ""),
        "bot_token": toml_data.get("bot_token", ""),
        "session_name": toml_data.get("session_name", ""),
    }
    for field, env_key in _ENV_KEYS.items():
        if env_key in env and env[env_key] != "":
            merged[field] = env[env_key]
    return merged


def load_settings(
    env: Mapping[str, str] | None = None,
    *,
    config_path: Path | None = None,
) -> Settings:
    environ = os.environ if env is None else env
    if config_path is not None:
        if not config_path.is_file():
            raise SettingsError(f"config not found: {config_path}")
        path = config_path
    else:
        path = _first_config_file()
    toml_data: dict[str, Any] = load_toml(path) if path is not None else {}
    values = _merge(toml_data, environ)
    return settings_from_values(source_path=path, **values)
