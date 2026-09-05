from collections.abc import Mapping

from tgytdlp.config import Settings
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers.callbacks import handle_callback
from tgytdlp.telegram.handlers.cookies import (
    document_from_message,
    handle_clear_cookies,
    handle_cookie_document,
    handle_cookies_help,
    handle_save_as_cookie,
    is_clear_cookies_command,
    is_cookies_command,
    is_save_as_cookie_command,
)
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
        if isinstance(chat_id, int):
            text = message.get("text")
            if isinstance(text, str):
                if is_start_command(text):
                    handle_start(api, chat_id)
                    return
                if is_cookies_command(text):
                    handle_cookies_help(api, settings.data_dir, chat_id)
                    return
                if is_clear_cookies_command(text):
                    handle_clear_cookies(api, settings.data_dir, chat_id)
                    return
                if is_save_as_cookie_command(text):
                    handle_save_as_cookie(api, settings.data_dir, chat_id, text)
                    return
                url = extract_url(text)
                if url is not None:
                    handle_url(api, settings, store, chat_id, url)
                    return
            document = document_from_message(message)
            if document is not None:
                handle_cookie_document(api, settings.data_dir, chat_id, document)
                return
        return
    query = _as_mapping(update.get("callback_query"))
    if query is not None:
        handle_callback(
            api,
            query,
            sample_dir=settings.data_dir / "samples",
            use_file_uri=settings.uses_local_file_uri,
            data_dir=settings.data_dir,
        )


def register_all(_api: BotAPI) -> None:
    return None
