import argparse
import logging
from pathlib import Path

from tgytdlp.jobs.files import JobError, read_job, write_result
from tgytdlp.jobs.files import ResultSpec
from tgytdlp.worker.opts import cookiefile_from_env
from tgytdlp.worker.ytdlp import run_download

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgytdlp-worker",
        description="Download worker (yt-dlp). Do not run in the chat process.",
        suggest_on_error=True,
    )
    parser.add_argument("--job", type=Path, required=True, help="job JSON path")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    try:
        job = read_job(args.job)
    except JobError as exc:
        logger.error("%s", exc)
        return 2
    try:
        downloaded = run_download(
            job.url,
            job.dest_dir,
            cookies=cookiefile_from_env(),
        )
    except Exception as exc:
        write_result(
            args.job,
            ResultSpec(
                job_id=job.job_id,
                ok=False,
                path=None,
                title=None,
                error=str(exc),
                result_path=args.job,
            ),
        )
        logger.error("download failed")
        return 1
    write_result(
        args.job,
        ResultSpec(
            job_id=job.job_id,
            ok=True,
            path=downloaded.path,
            title=downloaded.title,
            error=None,
            result_path=args.job,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
