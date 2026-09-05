from collections.abc import Mapping

from tgytdlp.telegram.api import BotAPI

START_TEXT = (
    "Send a public http(s) URL and I will fetch it in a separate worker, "
    "then send the file back here.\n\n"
    "If YouTube asks you to sign in, tap the YouTube button and send a "
    "login file. Use a button, or paste a link."
)

HOW_TEXT = (
    "1. Paste an http(s) URL.\n"
    "2. A worker process runs yt-dlp. This chat process never imports it.\n"
    "3. I send the file with sendDocument.\n"
    "4. If YouTube asks you to sign in, send a cookie.txt document. "
    "Tap “YouTube sign-in file” for the steps."
)


def start_keyboard() -> dict[str, object]:
    return {
        "inline_keyboard": [
            [{"text": "How it works", "callback_data": "how"}],
            [{"text": "YouTube sign-in file", "callback_data": "cookies"}],
            [{"text": "Send a sample file", "callback_data": "sample"}],
        ]
    }


def is_start_command(text: str) -> bool:
    first = text.split(maxsplit=1)[0]
    return first == "/start" or first.startswith("/start@")


def handle_start(api: BotAPI, chat_id: int) -> dict[str, object]:
    return api.send_message(chat_id, START_TEXT, reply_markup=start_keyboard())


def handle_how(api: BotAPI, chat_id: int) -> dict[str, object]:
    return api.send_message(chat_id, HOW_TEXT)


def _as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {str(key): item for key, item in value.items()}


def chat_id_from_message(message: Mapping[str, object]) -> int | None:
    chat = _as_mapping(message.get("chat"))
    if chat is None:
        return None
    raw = chat.get("id")
    return raw if isinstance(raw, int) else None
