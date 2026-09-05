from pathlib import Path

from tgytdlp.telegram.api import BotAPI


def send_document(
    api: BotAPI,
    chat_id: int,
    file_path: Path,
    *,
    use_file_uri: bool,
) -> dict[str, object]:
    resolved = file_path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    document = resolved.as_uri() if use_file_uri else str(resolved)
    return api.send_document(
        chat_id,
        document,
        use_file_uri=use_file_uri,
        filename=resolved.name,
    )
