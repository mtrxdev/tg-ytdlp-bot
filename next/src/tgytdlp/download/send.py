from pathlib import Path

from tgytdlp.telegram.api import BotAPI


def send_document(
    api: BotAPI,
    chat_id: int,
    file_path: Path,
    *,
    use_file_uri: bool,
    reply_to: int | None = None,
) -> dict[str, object]:
    resolved = file_path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    document = resolved.as_uri() if use_file_uri else str(resolved)
    reply = {"message_id": reply_to} if reply_to is not None else None
    return api.send_document(
        chat_id,
        document,
        use_file_uri=use_file_uri,
        filename=resolved.name,
        reply_parameters=reply,
    )
