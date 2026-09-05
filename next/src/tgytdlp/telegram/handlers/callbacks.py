from collections.abc import Mapping
from pathlib import Path

from tgytdlp.download.send import send_document
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers.cookies import handle_cookies_help
from tgytdlp.telegram.handlers.start import handle_how


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {str(key): item for key, item in value.items()}


def handle_callback(
    api: BotAPI,
    query: Mapping[str, object],
    *,
    sample_dir: Path,
    use_file_uri: bool,
    data_dir: Path | None = None,
) -> None:
    query_id = str(query.get("id", ""))
    data = str(query.get("data", ""))
    message = _as_mapping(query.get("message"))
    chat: Mapping[str, object] | None = None
    if message is not None:
        chat = _as_mapping(message.get("chat"))
    chat_id = chat.get("id") if chat is not None else None
    if query_id:
        api.answer_callback_query(query_id)
    if not isinstance(chat_id, int):
        return
    if data == "how":
        handle_how(api, chat_id)
        return
    if data == "cookies":
        handle_cookies_help(api, data_dir or sample_dir.parent, chat_id)
        return
    if data == "sample":
        sample_dir.mkdir(parents=True, exist_ok=True)
        sample = sample_dir / "tgytdlp-sample.txt"
        sample.write_text("sample file from the rewrite\n", encoding="utf-8")
        send_document(api, chat_id, sample, use_file_uri=use_file_uri)
