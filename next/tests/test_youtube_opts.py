from pathlib import Path

from tgytdlp.worker.opts import build_ydl_opts, cookiefile_from_env
from tgytdlp.worker.ytdlp import run_download
from tests.test_worker import FakeYDL


def test_build_ydl_opts_enables_node(tmp_path: Path) -> None:
    opts = build_ydl_opts(tmp_path / "out")
    assert opts["js_runtimes"] == {"node": {}}
    assert opts["noplaylist"] is True
    assert "cookiefile" not in opts


def test_build_ydl_opts_adds_existing_cookiefile(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    opts = build_ydl_opts(tmp_path / "out", cookies=cookies)
    assert opts["cookiefile"] == str(cookies)


def test_build_ydl_opts_skips_missing_cookiefile(tmp_path: Path) -> None:
    opts = build_ydl_opts(tmp_path / "out", cookies=tmp_path / "missing.txt")
    assert "cookiefile" not in opts


def test_cookiefile_from_env_requires_existing_file(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    assert cookiefile_from_env({"TG_COOKIES": str(cookies)}) == cookies
    assert cookiefile_from_env({"TG_COOKIES": str(tmp_path / "nope")}) is None
    assert cookiefile_from_env({}) is None


def test_run_download_passes_node_runtime(tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    class Capture(FakeYDL):
        def __init__(self, opts: dict[str, object]) -> None:
            super().__init__(opts)
            seen.update(opts)

    run_download("https://example.com/v", tmp_path / "out", ydl_cls=Capture)
    assert seen["js_runtimes"] == {"node": {}}
