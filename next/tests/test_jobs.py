from pathlib import Path

from tgytdlp.jobs.files import JobSpec, ResultSpec, new_job_id, read_job, read_result, write_job, write_result
from tgytdlp.jobs.spawn import build_worker_argv
from tgytdlp.store.sqlite import Store


def test_job_roundtrip(tmp_path: Path) -> None:
    job_id = new_job_id()
    path = tmp_path / "jobs" / f"{job_id}.json"
    spec = JobSpec(
        job_id=job_id,
        url="https://example.com/v",
        chat_id=7,
        dest_dir=tmp_path / "files" / job_id,
        path=path,
    )
    write_job(path, spec)
    loaded = read_job(path)
    assert loaded.url == spec.url
    assert loaded.chat_id == 7
    write_result(
        path,
        ResultSpec(
            job_id=job_id,
            ok=True,
            path=tmp_path / "out.mp4",
            title="clip",
            error=None,
            result_path=path,
        ),
    )
    result = read_result(path)
    assert result.ok is True
    assert result.title == "clip"


def test_worker_argv_uses_module(tmp_path: Path) -> None:
    job = tmp_path / "job.json"
    argv = build_worker_argv(job)
    assert argv[-3:] == ["-m", "tgytdlp.worker", "--job"] or argv[-2] == "--job"
    assert "-m" in argv
    assert "tgytdlp.worker" in argv


def test_store_offset_and_job(tmp_path: Path) -> None:
    store = Store(tmp_path / "bot.sqlite")
    try:
        assert store.get_offset() is None
        store.set_offset(11)
        assert store.get_offset() == 11
        store.upsert_job("abc", 1, "https://x", "queued")
        store.upsert_job("abc", 1, "https://x", "done", path="/tmp/a")
    finally:
        store.close()
