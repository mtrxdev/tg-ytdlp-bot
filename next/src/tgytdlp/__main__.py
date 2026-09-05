import logging
import sys

from pyrogram import idle

from tgytdlp.cli import parse_cli
from tgytdlp.config import SettingsError, load_settings
from tgytdlp.telegram import build_client, register_all

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    args = parse_cli(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        settings = load_settings(config_path=args.config)
    except SettingsError as exc:
        logger.error("%s", exc)
        return 2

    app = build_client(settings)
    if not args.check:
        register_all(app)

    app.start()
    try:
        me = app.get_me()
        label = f"@{me.username}" if me.username else str(me.id)
        print(label)
        if args.check:
            return 0
        logger.info("idle")
        idle()
    finally:
        app.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
