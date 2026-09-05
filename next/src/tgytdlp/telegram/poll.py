import logging
from collections.abc import Callable

from tgytdlp.config import Settings
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers import process_update

logger = logging.getLogger(__name__)

UpdateHandler = Callable[[BotAPI, Settings, Store, dict[str, object]], None]


def poll_once(
    api: BotAPI,
    settings: Settings,
    store: Store,
    *,
    handler: UpdateHandler = process_update,
) -> int:
    offset = store.get_offset()
    updates = api.get_updates(offset=offset, timeout=settings.poll_timeout)
    for update in updates:
        raw_id = update.get("update_id")
        if isinstance(raw_id, int):
            store.set_offset(raw_id + 1)
        handler(api, settings, store, update)
    return len(updates)


def run_forever(api: BotAPI, settings: Settings, store: Store) -> None:
    logger.info("long-polling getUpdates at %s", settings.api_base)
    while True:
        poll_once(api, settings, store)
