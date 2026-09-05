from collections.abc import Mapping
import os
from pathlib import Path


def cookiefile_from_env(env: Mapping[str, str] | None = None) -> Path | None:
    environ = os.environ if env is None else env
    raw = environ.get("TG_COOKIES", "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_file():
        return None
    return path


def build_ydl_opts(
    dest_dir: Path,
    *,
    cookies: Path | None = None,
) -> dict[str, object]:
    opts: dict[str, object] = {
        "outtmpl": str(dest_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "restrictfilenames": True,
        "noplaylist": True,
        "js_runtimes": {"node": {}},
    }
    if cookies is not None and cookies.is_file():
        opts["cookiefile"] = str(cookies)
    return opts
