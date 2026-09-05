import subprocess
import sys
from pathlib import Path


def build_worker_argv(job_path: Path) -> list[str]:
    return [sys.executable, "-m", "tgytdlp.worker", "--job", str(job_path)]


def run_job_process(job_path: Path, *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        build_worker_argv(job_path),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
