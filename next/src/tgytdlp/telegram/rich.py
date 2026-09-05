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
        footer("Buttons stay. Status lines disappear after the file arrives."),
    )


def how_rich(text: str) -> dict[str, object]:
    return rich_blocks(heading("How it works"), paragraph(text))


def cookies_rich(status: str, help_text: str) -> dict[str, object]:
    return rich_blocks(
        heading("YouTube sign-in file"),
        paragraph(status),
        numbered_list(
            [
                "Open YouTube in the browser where you are already signed in.",
                "Install Cookie-Editor or “Get cookies.txt LOCALLY”.",
                "Export cookies as a .txt file.",
                "Send that file here (paperclip → File). Not a screenshot.",
            ]
        ),
        footer(help_text),
    )


def progress_rich(title: str, body: str) -> dict[str, object]:
    return rich_blocks(heading(title), paragraph(body))


def dismiss_keyboard() -> dict[str, object]:
    return {"inline_keyboard": [[{"text": "Got it", "callback_data": "dismiss"}]]}
