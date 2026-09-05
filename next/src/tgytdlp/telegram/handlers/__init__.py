from collections.abc import Mapping

from tgytdlp.config import Settings
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers.callbacks import handle_callback
from tgytdlp.telegram.handlers.start import chat_id_from_message, handle_start, is_start_command
from tgytdlp.telegram.handlers.urls import extract_url, handle_url


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {str(key): item for key, item in value.items()}


def process_update(api: BotAPI, settings: Settings, store: Store, update: Mapping[str, object]) -> None:
    message = _as_mapping(update.get("message"))
    if message is not None:
        chat_id = chat_id_from_message(message)
        text = message.get("text")
        if isinstance(chat_id, int) and isinstance(text, str):
            if is_start_command(text):
                handle_start(api, chat_id)
                return
            url = extract_url(text)
            if url is not None:
                handle_url(api, settings, store, chat_id, url)
                return
        return
    query = _as_mapping(update.get("callback_query"))
    if query is not None:
        handle_callback(
            api,
            query,
            sample_dir=settings.data_dir / "samples",
            use_file_uri=settings.uses_local_file_uri,
        )


def register_all(_api: BotAPI) -> None:
    return None
