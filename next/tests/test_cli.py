import pytest

from tgytdlp.cli import parse_cli


def test_parse_cli_check_flag() -> None:
    args = parse_cli(["--check"])
    assert args.check is True
    assert args.config is None


def test_parse_cli_config_path() -> None:
    args = parse_cli(["--config", "settings.toml"])
    assert args.check is False
    assert args.config.name == "settings.toml"


def test_parse_cli_rejects_unknown() -> None:
    with pytest.raises(SystemExit):
        parse_cli(["--nope"])
