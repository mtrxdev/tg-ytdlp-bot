from pathlib import Path

import pytest

from tgytdlp.config import SettingsError, load_settings, settings_from_mapping


def _valid(**overrides: str) -> dict[str, str]:
    env = {
        "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
        "TG_API_BASE": "https://api.telegram.org",
        "TG_DATA_DIR": "data",
        "TG_POLL_TIMEOUT": "25",
        "TG_WORKER_TIMEOUT": "60",
    }
    env.update(overrides)
    return env


def test_settings_from_mapping_reads_fields(tmp_path: Path) -> None:
    settings = settings_from_mapping(
        _valid(TG_DATA_DIR=str(tmp_path / "d")),
        source_path=tmp_path / "settings.toml",
        relative_to=tmp_path,
    )
    assert settings.bot_token.endswith("xx")
    assert settings.api_base == "https://api.telegram.org"
    assert settings.poll_timeout == 25
    assert "***" in repr(settings)
    assert settings.bot_token not in repr(settings)


def test_settings_defaults(tmp_path: Path) -> None:
    settings = settings_from_mapping(
        {"TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx"},
        relative_to=tmp_path,
    )
    assert settings.api_base == "https://api.telegram.org"
    assert settings.data_dir == (tmp_path / "data").resolve()
    assert settings.poll_timeout == 25
    assert settings.uses_local_file_uri is False
    assert settings.cookies is None


def test_local_api_base_uses_file_uri() -> None:
    settings = settings_from_mapping(
        {
            "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
            "TG_API_BASE": "http://127.0.0.1:8081",
        }
    )
    assert settings.uses_local_file_uri is True


@pytest.mark.parametrize(
    "key,value",
    [
        ("TG_BOT_TOKEN", ""),
        ("TG_BOT_TOKEN", "not-a-token"),
        ("TG_API_BASE", "ftp://nope"),
        ("TG_POLL_TIMEOUT", "0"),
        ("TG_POLL_TIMEOUT", "x"),
    ],
)
def test_settings_rejects_bad_values(key: str, value: str) -> None:
    with pytest.raises(SettingsError):
        settings_from_mapping(_valid(**{key: value}))


def test_load_settings_reads_toml(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        "\n".join(
            [
                'bot_token = "1234567890:AAExampleTokenValue_12-xx"',
                'api_base = "http://127.0.0.1:8081"',
                'data_dir = "state"',
                "poll_timeout = 30",
            ]
        ),
        encoding="utf-8",
    )
    settings = load_settings({}, config_path=path)
    assert settings.api_base == "http://127.0.0.1:8081"
    assert settings.data_dir == tmp_path / "state"
    assert settings.poll_timeout == 30
    assert settings.source_path == path


def test_env_overrides_toml(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        'bot_token = "1234567890:AAExampleTokenValue_12-xx"\napi_base = "https://api.telegram.org"\n',
        encoding="utf-8",
    )
    settings = load_settings(
        {"TG_API_BASE": "http://127.0.0.1:9"},
        config_path=path,
    )
    assert settings.api_base == "http://127.0.0.1:9"


def test_settings_reads_cookies_path(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    settings = settings_from_mapping(
        _valid(TG_COOKIES=str(cookies)),
        relative_to=tmp_path,
    )
    assert settings.cookies == cookies


def test_missing_explicit_config_raises(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="not found"):
        load_settings({}, config_path=tmp_path / "missing.toml")
