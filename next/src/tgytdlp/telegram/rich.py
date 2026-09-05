from collections.abc import Sequence


def heading(text: str, size: int = 2) -> dict[str, object]:
    return {"type": "heading", "text": text, "size": size}


def paragraph(text: str) -> dict[str, object]:
    return {"type": "paragraph", "text": text}


def divider() -> dict[str, object]:
    return {"type": "divider"}


def footer(text: str) -> dict[str, object]:
    return {"type": "footer", "text": text}


def numbered_list(items: Sequence[str]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for index, item in enumerate(items, start=1):
        entries.append(
            {
                "blocks": [paragraph(item)],
                "value": index,
                "type": "1",
            }
        )
    return {"type": "list", "items": entries}


def rich_blocks(*blocks: dict[str, object]) -> dict[str, object]:
    return {"blocks": list(blocks)}


def notice_rich(title: str, body: str) -> dict[str, object]:
    return rich_blocks(heading(title), paragraph(body))


def start_rich(text: str) -> dict[str, object]:
    return rich_blocks(
        heading("Send a link"),
        paragraph(text),
        divider(),
        footer("I react to your link and use Telegram’s uploading status. No leftover wait lines."),
    )


def how_rich(text: str) -> dict[str, object]:
    return rich_blocks(heading("How it works"), paragraph(text))


def cookies_rich(status: str, help_text: str) -> dict[str, object]:
    return rich_blocks(
        heading("YouTube sign-in file"),
        paragraph(status),
        numbered_list(
            [
                "On a computer, open YouTube in the browser where you are already signed in.",
                "Install Cookie-Editor or “Get cookies.txt LOCALLY” in that computer browser. Phone Chrome and Safari cannot install it.",
                "Export cookies as a .txt file.",
                "Send that file in this chat (paperclip → File). You can send it from your phone. Not a screenshot.",
            ]
        ),
        footer(help_text),
    )


def thinking(text: str) -> dict[str, object]:
    return {"type": "thinking", "text": text}


def checkbox_list(items: Sequence[str], checked_through: int) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for index, item in enumerate(items):
        entries.append(
            {
                "blocks": [paragraph(item)],
                "has_checkbox": True,
                "is_checked": index <= checked_through,
            }
        )
    return {"type": "list", "items": entries}


DRAFT_STEPS = ("Got your link", "Fetching the file", "Sending it here")


def draft_rich(step: int, *, host: str) -> dict[str, object]:
    clamped = min(max(step, 0), 2)
    thoughts = (
        f"Opening {host}",
        f"Fetching from {host}",
        "Sending the file",
    )
    return rich_blocks(thinking(thoughts[clamped]), checkbox_list(DRAFT_STEPS, clamped))


def progress_rich(title: str, body: str) -> dict[str, object]:
    return rich_blocks(heading(title), paragraph(body))


def dismiss_keyboard() -> dict[str, object]:
    return {"inline_keyboard": [[{"text": "Got it", "callback_data": "dismiss"}]]}
