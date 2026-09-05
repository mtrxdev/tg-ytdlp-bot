import shutil
from pathlib import Path

from tgytdlp.jobs.files import JobSpec, result_path_for


def cleanup_job_workspace(spec: JobSpec) -> None:
    dest = spec.dest_dir
    if dest.is_dir():
        shutil.rmtree(dest, ignore_errors=True)
    for path in (spec.path, result_path_for(spec.path)):
        if path.is_file():
            path.unlink(missing_ok=True)


def cleanup_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
        return
    if path.is_file():
        path.unlink(missing_ok=True)
