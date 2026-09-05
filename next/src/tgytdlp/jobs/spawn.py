import os
import subprocess
import sys
from pathlib import Path


def build_worker_argv(job_path: Path) -> list[str]:
    return [sys.executable, "-m", "tgytdlp.worker", "--job", str(job_path)]


def run_job_process(
    job_path: Path,
    *,
    timeout: int,
    cookies: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if cookies is not None:
        env["TG_COOKIES"] = str(cookies)
    return subprocess.run(
        build_worker_argv(job_path),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
