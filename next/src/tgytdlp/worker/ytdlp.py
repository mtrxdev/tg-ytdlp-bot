from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class YoutubeDLLike(Protocol):
    def __enter__(self) -> "YoutubeDLLike": ...

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        tb: object,
    ) -> bool | None: ...

    def extract_info(self, url: str, download: bool = True) -> object: ...

    def prepare_filename(self, info: object) -> str: ...

    def sanitize_info(self, info: object) -> object: ...


YdlFactory = Callable[[dict[str, object]], YoutubeDLLike]


@dataclass(frozen=True)
class DownloadResult:
    path: Path
    title: str | None


def _default_ydl(opts: dict[str, object]) -> YoutubeDLLike:
    from yt_dlp import YoutubeDL

    return YoutubeDL(opts)


def _filepath_from_info(info: object, ydl: YoutubeDLLike) -> Path:
    if isinstance(info, dict):
        requested = info.get("requested_downloads")
        if isinstance(requested, list) and requested:
            first = requested[0]
            if isinstance(first, dict):
                raw = first.get("filepath") or first.get("filename")
                if isinstance(raw, str) and raw:
                    return Path(raw)
        raw_path = info.get("filepath")
        if isinstance(raw_path, str) and raw_path:
            return Path(raw_path)
    prepared = ydl.prepare_filename(info)
    return Path(prepared)


def run_download(
    url: str,
    dest_dir: Path,
    *,
    ydl_cls: YdlFactory | None = None,
) -> DownloadResult:
    dest_dir.mkdir(parents=True, exist_ok=True)
    factory = ydl_cls or _default_ydl
    opts: dict[str, object] = {
        "outtmpl": str(dest_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "restrictfilenames": True,
    }
    with factory(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if hasattr(ydl, "sanitize_info"):
            ydl.sanitize_info(info)
        path = _filepath_from_info(info, ydl)
        title: str | None = None
        if isinstance(info, dict) and isinstance(info.get("title"), str):
            title = info["title"]
    if not path.is_file():
        raise FileNotFoundError(f"yt-dlp produced no file: {path}")
    return DownloadResult(path=path, title=title)
