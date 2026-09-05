import logging

from tgytdlp.cli import parse_cli
from tgytdlp.config import SettingsError, load_settings
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPIError, build_api
from tgytdlp.telegram.poll import run_forever
from tgytdlp.telegram.webhook import webhook_secret

logger = logging.getLogger(__name__)


def _identity_label(me: dict[str, object]) -> str:
    username = me.get("username")
    if isinstance(username, str) and username:
        return f"@{username}"
    user_id = me.get("id")
    return str(user_id)


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

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    api = build_api(settings)
    try:
        me = api.get_me()
    except BotAPIError as exc:
        logger.error("%s", exc)
        return 1
    print(_identity_label(me))
    if args.check:
        return 0
    if args.delete_webhook:
        try:
            api.delete_webhook()
        except BotAPIError as exc:
            logger.error("%s", exc)
            return 1
        print("webhook deleted")
        return 0
    if args.set_webhook:
        try:
            api.set_webhook(args.set_webhook, secret_token=webhook_secret(settings))
        except BotAPIError as exc:
            logger.error("%s", exc)
            return 1
        print("webhook set")
        return 0

    store = Store(settings.data_dir / "bot.sqlite")
    try:
        run_forever(api, settings, store)
    except KeyboardInterrupt:
        logger.info("stopped")
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
