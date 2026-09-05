import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAP = REPO / "next" / "docs" / "rename-map.md"
NEW_FILE = re.compile(r"next/src/tgytdlp/[a-z0-9_./]+\.py")


def _rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in MAP.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 2:
            continue
        rows.append((cells[0].strip("`"), cells[1]))
    return rows


def test_rename_map_has_magic_and_start() -> None:
    olds = {old for old, _ in _rows()}
    news = "\n".join(new for _, new in _rows())
    assert "magic.py" in olds
    assert "CONFIG/_config.py" in olds
    assert "COMMANDS/format_cmd.py" in olds
    assert "next/src/tgytdlp/__main__.py" in news
    assert "telegram/handlers/format.py" in news


def test_old_concrete_files_still_exist() -> None:
    missing: list[str] = []
    for old, _new in _rows():
        if "*" in old or "XX" in old:
            continue
        if old in {"CONFIG/config.py"}:
            continue
        path = REPO / old
        if not path.is_file():
            missing.append(old)
    assert missing == []


def test_new_module_targets_are_unique() -> None:
    targets = []
    for _old, new in _rows():
        targets.extend(NEW_FILE.findall(new))
    assert targets
    assert len(targets) == len(set(targets))
