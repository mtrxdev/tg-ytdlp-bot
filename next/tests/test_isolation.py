import ast
import sys
from pathlib import Path

CHAT_ROOT = Path(__file__).resolve().parents[1] / "src" / "tgytdlp"
SKIP_DIRS = {"worker"}


def test_chat_sources_do_not_import_ytdlp() -> None:
    offenders: list[str] = []
    for path in CHAT_ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.relative_to(CHAT_ROOT).parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "yt_dlp" or alias.name.startswith("yt_dlp."):
                        offenders.append(str(path))
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "yt_dlp" or node.module.startswith("yt_dlp."):
                    offenders.append(str(path))
    assert offenders == []


def test_importing_chat_modules_does_not_load_ytdlp() -> None:
    sys.modules.pop("yt_dlp", None)
    import tgytdlp.config  # noqa: F401
    import tgytdlp.cookies  # noqa: F401
    import tgytdlp.jobs  # noqa: F401
    import tgytdlp.telegram.api  # noqa: F401
    import tgytdlp.telegram.handlers  # noqa: F401
    import tgytdlp.telegram.poll  # noqa: F401
    import tgytdlp.telegram.webhook  # noqa: F401
    import tgytdlp.download.send  # noqa: F401

    assert "yt_dlp" not in sys.modules
