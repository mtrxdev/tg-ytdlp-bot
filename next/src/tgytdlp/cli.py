from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgytdlp",
        description="Telegram download bot rewrite",
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
    return parser


def parse_cli(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
