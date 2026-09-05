from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.rich import how_rich, start_rich
from tgytdlp.telegram.status import Status, send_status

START_TEXT = (
    "Send a public http(s) URL and I will fetch it in a separate worker, "
    "then send the file back here.\n\n"
    "If YouTube asks you to sign in, tap the YouTube button and send a "
    "login file. Use a button, or paste a link."
)

HOW_TEXT = (
    "1. Paste an http(s) URL. I react to that message.\n"
    "2. Telegram shows the bot uploading a file. A short draft lists the steps.\n"
    "3. The file arrives as a reply. The draft goes away. No leftover wait line.\n"
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
    return api.send_rich_message(
        chat_id,
        start_rich(START_TEXT),
        reply_markup=start_keyboard(),
    )


def handle_how(
    api: BotAPI,
    chat_id: int,
    *,
    user_id: int | None = None,
    query_id: str | None = None,
) -> Status:
    return send_status(
        api,
        chat_id,
        how_rich(HOW_TEXT),
        user_id=user_id,
        query_id=query_id,
        dismissable=True,
    )
