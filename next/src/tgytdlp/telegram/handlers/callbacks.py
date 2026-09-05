from collections.abc import Mapping
from pathlib import Path

from tgytdlp.download.send import send_document
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers.cookies import handle_cookies_help
from tgytdlp.telegram.handlers.start import handle_how
from tgytdlp.telegram.ids import as_mapping, chat_id_from_message, int_field, user_id_from
from tgytdlp.telegram.status import sweep_messages


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
    message = as_mapping(query.get("message"))
    chat_id = chat_id_from_message(message) if message is not None else None
    user_id = user_id_from(query)
    if query_id:
        api.answer_callback_query(query_id)
    if not isinstance(chat_id, int):
        return
    if data == "dismiss":
        mid = int_field(message, "message_id") if message is not None else None
        sweep_messages(api, chat_id, [mid], private_only=False)
        return
    if data == "how":
        handle_how(api, chat_id, user_id=user_id, query_id=query_id or None)
        return
    if data == "cookies":
        handle_cookies_help(
            api,
            data_dir or sample_dir.parent,
            chat_id,
            user_id=user_id,
            query_id=query_id or None,
        )
        return
    if data == "sample":
        sample_dir.mkdir(parents=True, exist_ok=True)
        sample = sample_dir / "tgytdlp-sample.txt"
        sample.write_text("sample file from the rewrite\n", encoding="utf-8")
        send_document(api, chat_id, sample, use_file_uri=use_file_uri)
