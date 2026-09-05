from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{20,}$")


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    session_name: str
    env_path: Path | None


def _next_root() -> Path:
    return Path(__file__).resolve().parents[3]


def env_candidates() -> tuple[Path, ...]:
    override = os.environ.get("TG_YTDLP_ENV")
    if override:
        return (Path(override),)
    return (Path.cwd() / ".env", _next_root() / ".env")


def load_dotenv_files() -> Path | None:
    for path in env_candidates():
        if path.is_file():
            load_dotenv(path, override=False)
            return path
    return None


def settings_from_mapping(
    env: dict[str, str],
    *,
    env_path: Path | None = None,
) -> Settings:
    raw_id = (env.get("TG_API_ID") or "").strip()
    api_hash = (env.get("TG_API_HASH") or "").strip()
    bot_token = (env.get("TG_BOT_TOKEN") or "").strip()
    session_name = (env.get("TG_SESSION_NAME") or "tgytdlp").strip() or "tgytdlp"

    if not raw_id.isdigit():
        raise SettingsError("TG_API_ID must be a positive integer")
    api_id = int(raw_id)
    if api_id <= 0:
        raise SettingsError("TG_API_ID must be a positive integer")
    if len(api_hash) < 8:
        raise SettingsError("TG_API_HASH is missing or too short")
    if not _TOKEN_RE.match(bot_token):
        raise SettingsError("TG_BOT_TOKEN is not a bot token")

    return Settings(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        session_name=session_name,
        env_path=env_path,
    )


def load_settings() -> Settings:
    env_path = load_dotenv_files()
    return settings_from_mapping(dict(os.environ), env_path=env_path)
