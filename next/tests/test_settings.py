from pathlib import Path

import pytest

from tgytdlp.config import SettingsError, load_settings, settings_from_mapping


def _valid(**overrides: str) -> dict[str, str]:
    env = {
        "TG_API_ID": "12345678",
        "TG_API_HASH": "0123456789abcdef",
        "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
        "TG_SESSION_NAME": "probe",
    }
    env.update(overrides)
    return env


def test_settings_from_mapping_reads_fields() -> None:
    settings = settings_from_mapping(_valid(), source_path=Path("/tmp/x.toml"))
    assert settings.api_id == 12345678
    assert settings.api_hash == "0123456789abcdef"
    assert settings.session_name == "probe"
    assert settings.source_path == Path("/tmp/x.toml")


def test_settings_default_session_name() -> None:
    env = _valid()
    del env["TG_SESSION_NAME"]
    settings = settings_from_mapping(env)
    assert settings.session_name == "tgytdlp"


@pytest.mark.parametrize(
    "key,value",
    [
        ("TG_API_ID", ""),
        ("TG_API_ID", "0"),
        ("TG_API_ID", "-1"),
        ("TG_API_ID", "abc"),
        ("TG_API_HASH", ""),
        ("TG_API_HASH", "short"),
        ("TG_BOT_TOKEN", ""),
        ("TG_BOT_TOKEN", "not-a-token"),
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
                "api_id = 12345678",
                'api_hash = "0123456789abcdef"',
                'bot_token = "1234567890:AAExampleTokenValue_12-xx"',
                'session_name = "from_toml"',
            ]
        ),
        encoding="utf-8",
    )
    settings = load_settings({}, config_path=path)
    assert settings.api_id == 12345678
    assert settings.session_name == "from_toml"
    assert settings.source_path == path


def test_env_overrides_toml(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        "\n".join(
            [
                "api_id = 111",
                'api_hash = "0123456789abcdef"',
                'bot_token = "1234567890:AAExampleTokenValue_12-xx"',
                'session_name = "from_toml"',
            ]
        ),
        encoding="utf-8",
    )
    settings = load_settings(
        {"TG_SESSION_NAME": "from_env"},
        config_path=path,
    )
    assert settings.api_id == 111
    assert settings.session_name == "from_env"


def test_missing_explicit_config_raises(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="not found"):
        load_settings({}, config_path=tmp_path / "missing.toml")
