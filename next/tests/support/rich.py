from collections.abc import Mapping


def flatten_rich(rich: Mapping[str, object]) -> str:
    parts: list[str] = []
    blocks = rich.get("blocks")
    if not isinstance(blocks, list):
        return ""
    for block in blocks:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str):
            parts.append(text)
        items = block.get("items")
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                nested = item.get("blocks")
                if not isinstance(nested, list):
                    continue
                for inner in nested:
                    if isinstance(inner, dict) and isinstance(inner.get("text"), str):
                        parts.append(str(inner["text"]))
    return "\n".join(parts)


def last_rich_text(calls: list[dict[str, object]]) -> str:
    for call in reversed(calls):
        if call.get("method") != "sendRichMessage":
            continue
        body = call.get("body")
        if not isinstance(body, dict):
            continue
        rich = body.get("rich_message")
        if isinstance(rich, dict):
            return flatten_rich(rich)
    return ""
