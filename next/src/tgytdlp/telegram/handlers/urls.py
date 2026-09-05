from collections.abc import Callable
from pathlib import Path

from tgytdlp.config import Settings
from tgytdlp.cookies import resolve_cookies
from tgytdlp.download.errors import user_download_error
from tgytdlp.download.send import send_document
from tgytdlp.jobs.files import JobSpec, new_job_id, read_result, write_job
from tgytdlp.jobs.spawn import run_job_process
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI

JobRunner = Callable[[Path, int], None]


def extract_url(text: str) -> str | None:
    for part in text.split():
        if part.startswith("https://") or part.startswith("http://"):
            return part
    return None


def default_runner(job_path: Path, timeout: int, *, cookies: Path | None = None) -> None:
    run_job_process(job_path, timeout=timeout, cookies=cookies)


def handle_url(
    api: BotAPI,
    settings: Settings,
    store: Store,
    chat_id: int,
    url: str,
    *,
    runner: JobRunner = default_runner,
) -> None:
    job_id = new_job_id()
    dest_dir = settings.data_dir / "files" / job_id
    job_path = settings.data_dir / "jobs" / f"{job_id}.json"
    spec = JobSpec(
        job_id=job_id,
        url=url,
        chat_id=chat_id,
        dest_dir=dest_dir,
        path=job_path,
    )
    write_job(job_path, spec)
    store.upsert_job(job_id, chat_id, url, "queued")
    api.send_chat_action(chat_id, "upload_document")
    api.send_message(chat_id, "Downloading in a worker process…")
    try:
        cookies = resolve_cookies(settings.data_dir, chat_id, settings.cookies)
        if runner is default_runner:
            default_runner(job_path, settings.worker_timeout, cookies=cookies)
        else:
            runner(job_path, settings.worker_timeout)
    except Exception as exc:
        store.upsert_job(job_id, chat_id, url, "failed", error=str(exc))
        api.send_message(chat_id, "The worker did not finish. Try another URL.")
        return
    result = read_result(job_path)
    if not result.ok or result.path is None:
        store.upsert_job(job_id, chat_id, url, "failed", error=result.error)
        api.send_message(chat_id, user_download_error(result.error))
        return
    store.upsert_job(job_id, chat_id, url, "done", path=str(result.path))
    send_document(
        api,
        chat_id,
        result.path,
        use_file_uri=settings.uses_local_file_uri,
    )
