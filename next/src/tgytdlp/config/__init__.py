import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
import tomllib

_TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{20,}$")
_DEFAULT_API_BASE = "https://api.telegram.org"
_ENV_KEYS = {
    "bot_token": "TG_BOT_TOKEN",
    "api_base": "TG_API_BASE",
    "data_dir": "TG_DATA_DIR",
    "poll_timeout": "TG_POLL_TIMEOUT",
    "worker_timeout": "TG_WORKER_TIMEOUT",
    "cookies": "TG_COOKIES",
}


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    api_base: str
    data_dir: Path
    poll_timeout: int
    worker_timeout: int
    cookies: Path | None
    source_path: Path | None

    @property
    def uses_local_file_uri(self) -> bool:
        host = self.api_base.lower()
        return "api.telegram.org" not in host

    def __repr__(self) -> str:
        return (
            "Settings("
            f"bot_token='***', api_base={self.api_base!r}, "
            f"data_dir={self.data_dir!r}, poll_timeout={self.poll_timeout}, "
            f"worker_timeout={self.worker_timeout}, "
            f"cookies={'set' if self.cookies else None}, "
            f"source_path={self.source_path!r})"
        )


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


def load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise SettingsError("settings.toml must be a table")
    return {str(key): value for key, value in data.items()}


def settings_from_mapping(
    env: Mapping[str, str],
    *,
    source_path: Path | None = None,
    relative_to: Path | None = None,
) -> Settings:
    return settings_from_values(
        bot_token=env.get("TG_BOT_TOKEN", ""),
        api_base=env.get("TG_API_BASE", ""),
        data_dir=env.get("TG_DATA_DIR", ""),
        poll_timeout=env.get("TG_POLL_TIMEOUT", ""),
        worker_timeout=env.get("TG_WORKER_TIMEOUT", ""),
        cookies=env.get("TG_COOKIES", ""),
        source_path=source_path,
        relative_to=relative_to,
    )


def _as_int(value: object, name: str, default: int, *, minimum: int) -> int:
    if value is None or value == "":
        return default
    try:
        parsed = int(str(value).strip())
    except ValueError as exc:
        raise SettingsError(f"{name} must be an integer") from exc
    if parsed < minimum:
        raise SettingsError(f"{name} must be >= {minimum}")
    return parsed


def settings_from_values(
    *,
    bot_token: object,
    api_base: object = "",
    data_dir: object = "",
    poll_timeout: object = "",
    worker_timeout: object = "",
    cookies: object = "",
    source_path: Path | None = None,
    relative_to: Path | None = None,
) -> Settings:
    token_text = str(bot_token).strip()
    if not _TOKEN_RE.match(token_text):
        raise SettingsError("bot_token is not a bot token")

    base = str(api_base).strip() or _DEFAULT_API_BASE
    if not (base.startswith("http://") or base.startswith("https://")):
        raise SettingsError("api_base must be an http(s) URL")
    base = base.rstrip("/")

    raw_dir = str(data_dir).strip() or "data"
    path = Path(raw_dir)
    if not path.is_absolute():
        root = relative_to or (source_path.parent if source_path else Path.cwd())
        path = (root / path).resolve()

    cookie_text = str(cookies).strip()
    cookie_path: Path | None = None
    if cookie_text:
        cookie_path = Path(cookie_text)
        if not cookie_path.is_absolute():
            root = relative_to or (source_path.parent if source_path else Path.cwd())
            cookie_path = (root / cookie_path).resolve()

    return Settings(
        bot_token=token_text,
        api_base=base,
        data_dir=path,
        poll_timeout=_as_int(poll_timeout, "poll_timeout", 25, minimum=1),
        worker_timeout=_as_int(worker_timeout, "worker_timeout", 600, minimum=1),
        cookies=cookie_path,
        source_path=source_path,
    )


def _merge(toml_data: Mapping[str, object], env: Mapping[str, str]) -> dict[str, object]:
    merged: dict[str, object] = {
        "bot_token": toml_data.get("bot_token", ""),
        "api_base": toml_data.get("api_base", ""),
        "data_dir": toml_data.get("data_dir", ""),
        "poll_timeout": toml_data.get("poll_timeout", ""),
        "worker_timeout": toml_data.get("worker_timeout", ""),
        "cookies": toml_data.get("cookies", ""),
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
    toml_data: dict[str, object] = load_toml(path) if path is not None else {}
    values = _merge(toml_data, environ)
    relative_to = path.parent if path is not None else Path.cwd()
    return settings_from_values(source_path=path, relative_to=relative_to, **values)
