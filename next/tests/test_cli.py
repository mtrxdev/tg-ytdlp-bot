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


def test_parse_cli_webhook_flags() -> None:
    set_args = parse_cli(["--set-webhook", "https://example.vercel.app/api/telegram"])
    assert set_args.set_webhook == "https://example.vercel.app/api/telegram"
    assert set_args.delete_webhook is False
    delete_args = parse_cli(["--delete-webhook"])
    assert delete_args.delete_webhook is True
    assert delete_args.set_webhook is None


def test_parse_cli_rejects_unknown() -> None:
    with pytest.raises(SystemExit):
        parse_cli(["--nope"])
