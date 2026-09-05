import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgytdlp",
        description="Telegram download bot rewrite",
        suggest_on_error=True,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="connect, print identity, then exit",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="TOML settings file (default: settings.toml)",
    )
    parser.add_argument(
        "--set-webhook",
        metavar="URL",
        help="register a Bot API webhook URL and exit",
    )
    parser.add_argument(
        "--delete-webhook",
        action="store_true",
        help="remove the Bot API webhook and exit",
    )
    return parser


def parse_cli(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
