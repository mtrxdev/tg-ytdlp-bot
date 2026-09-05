from pathlib import Path

from tgytdlp.jobs.files import JobSpec, read_result, write_job
from tgytdlp.worker import __main__ as worker_main
from tgytdlp.worker.ytdlp import DownloadResult, run_download


class FakeYDL:
    def __init__(self, opts: dict[str, object]) -> None:
        self.opts = opts
        template = str(opts["outtmpl"])
        self.dest = Path(template).parent

    def __enter__(self) -> "FakeYDL":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def extract_info(self, url: str, download: bool = True) -> dict[str, object]:
        path = self.dest / "clip.bin"
        path.write_bytes(b"media")
        return {
            "id": "clip",
            "ext": "bin",
            "title": "clip",
            "requested_downloads": [{"filepath": str(path)}],
        }

    def prepare_filename(self, info: object) -> str:
        return str(self.dest / "clip.bin")

    def sanitize_info(self, info: object) -> object:
        return info


def test_run_download_with_fake_ydl(tmp_path: Path) -> None:
    result = run_download("https://example.com/v", tmp_path / "out", ydl_cls=FakeYDL)
    assert result.path.is_file()
    assert result.title == "clip"


def test_worker_main_writes_result(tmp_path: Path, monkeypatch: object) -> None:
    def fake_run(
        url: str,
        dest_dir: Path,
        ydl_cls: object = None,
        cookies: object = None,
    ) -> DownloadResult:
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / "out.bin"
        path.write_bytes(b"x")
        return DownloadResult(path=path, title="t")

    monkeypatch.setattr("tgytdlp.worker.__main__.run_download", fake_run)
    job_path = tmp_path / "job.json"
    write_job(
        job_path,
        JobSpec(
            job_id="abc123",
            url="https://example.com/v",
            chat_id=1,
            dest_dir=tmp_path / "files",
            path=job_path,
        ),
    )
    assert worker_main.main(["--job", str(job_path)]) == 0
    result = read_result(job_path)
    assert result.ok is True
    assert result.path is not None
    assert result.path.is_file()
