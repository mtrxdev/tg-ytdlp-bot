from pathlib import Path

import pytest

from tgytdlp.config import SettingsError, settings_from_mapping


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
    settings = settings_from_mapping(_valid(), env_path=Path("/tmp/x.env"))
    assert settings.api_id == 12345678
    assert settings.api_hash == "0123456789abcdef"
    assert settings.session_name == "probe"
    assert settings.env_path == Path("/tmp/x.env")


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
