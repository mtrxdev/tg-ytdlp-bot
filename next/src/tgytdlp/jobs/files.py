import json
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class JobError(ValueError):
    pass


@dataclass(frozen=True)
class JobSpec:
    job_id: str
    url: str
    chat_id: int
    dest_dir: Path
    path: Path


@dataclass(frozen=True)
class ResultSpec:
    job_id: str
    ok: bool
    path: Path | None
    title: str | None
    error: str | None
    result_path: Path


def new_job_id() -> str:
    return uuid.uuid4().hex


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise JobError(f"missing job file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise JobError("job file must be an object")
    return {str(key): value for key, value in data.items()}


def write_job(path: Path, spec: JobSpec) -> None:
    _write_json(
        path,
        {
            "id": spec.job_id,
            "url": spec.url,
            "chat_id": spec.chat_id,
            "dest_dir": str(spec.dest_dir),
        },
    )


def read_job(path: Path) -> JobSpec:
    data = _read_json(path)
    job_id = str(data.get("id", "")).strip()
    url = str(data.get("url", "")).strip()
    dest = str(data.get("dest_dir", "")).strip()
    chat_raw = data.get("chat_id")
    if not job_id or not url or not dest:
        raise JobError("job file is missing id, url, or dest_dir")
    if not isinstance(chat_raw, int):
        raise JobError("job file chat_id must be an integer")
    return JobSpec(
        job_id=job_id,
        url=url,
        chat_id=chat_raw,
        dest_dir=Path(dest),
        path=path,
    )


def result_path_for(job_path: Path) -> Path:
    return job_path.with_name(job_path.name + ".result.json")


def write_result(job_path: Path, result: ResultSpec) -> None:
    _write_json(
        result_path_for(job_path),
        {
            "id": result.job_id,
            "ok": result.ok,
            "path": str(result.path) if result.path is not None else None,
            "title": result.title,
            "error": result.error,
        },
    )


def read_result(job_path: Path) -> ResultSpec:
    path = result_path_for(job_path)
    data = _read_json(path)
    raw_path = data.get("path")
    return ResultSpec(
        job_id=str(data.get("id", "")),
        ok=data.get("ok") is True,
        path=Path(str(raw_path)) if isinstance(raw_path, str) and raw_path else None,
        title=str(data["title"]) if isinstance(data.get("title"), str) else None,
        error=str(data["error"]) if isinstance(data.get("error"), str) else None,
        result_path=path,
    )
