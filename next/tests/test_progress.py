from tgytdlp.telegram.progress import draft_id_for, host_of
from tgytdlp.telegram.rich import DRAFT_STEPS, draft_rich
from tests.support.rich import flatten_rich


def test_draft_id_and_host() -> None:
    assert draft_id_for("abcd1234ffff") != 0
    assert host_of("https://www.youtube.com/watch?v=x") == "youtube.com"
    assert host_of("not-a-url") == "the link"


def test_draft_rich_has_thinking_and_checkboxes() -> None:
    rich = draft_rich(1, host="cdn.jsdelivr.net")
    text = flatten_rich(rich)
    assert "Fetching from cdn.jsdelivr.net" in text
    for step in DRAFT_STEPS:
        assert step in text
    blocks = rich["blocks"]
    assert isinstance(blocks, list)
    thinking = blocks[0]
    assert isinstance(thinking, dict)
    assert thinking["type"] == "thinking"
    listing = blocks[1]
    assert isinstance(listing, dict)
    items = listing["items"]
    assert isinstance(items, list)
    first = items[0]
    second = items[1]
    third = items[2]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    assert isinstance(third, dict)
    assert first["is_checked"] is True
    assert second["is_checked"] is True
    assert third["is_checked"] is False
