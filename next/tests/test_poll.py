from pathlib import Path
from tempfile import TemporaryDirectory

from tgytdlp.config import settings_from_mapping
from tgytdlp.jobs.files import ResultSpec, read_job, write_result
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers import process_update
from tgytdlp.telegram.handlers.urls import handle_url
from tgytdlp.telegram.poll import poll_once
from tests.support.botapi import FakeBotAPI
from tests.support.rich import last_rich_text


def _settings(tmp_path: Path, base: str) -> object:
    return settings_from_mapping(
        {
            "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
            "TG_API_BASE": base,
            "TG_DATA_DIR": str(tmp_path / "data"),
            "TG_POLL_TIMEOUT": "1",
        },
        relative_to=tmp_path,
    )


def test_poll_start_and_sample(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = _settings(tmp_path, fake.base_url)
        settings.data_dir.mkdir(parents=True)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        fake.push_update(
            {
                "update_id": 1,
                "message": {"chat": {"id": 10}, "text": "/start"},
            }
        )
        assert poll_once(api, settings, store) == 1
        assert store.get_offset() == 2
        fake.push_update(
            {
                "update_id": 2,
                "callback_query": {
                    "id": "cb1",
                    "data": "sample",
                    "message": {"chat": {"id": 10}},
                },
            }
        )
        poll_once(api, settings, store)
        fake.push_update(
            {
                "update_id": 3,
                "callback_query": {
                    "id": "cb2",
                    "data": "cookies",
                    "message": {"chat": {"id": 10}},
                },
            }
        )
        poll_once(api, settings, store)
        methods = [str(call["method"]) for call in fake.calls]
        assert "sendRichMessage" in methods
        assert "answerCallbackQuery" in methods
        assert "sendDocument" in methods
        text = last_rich_text(fake.calls)
        assert "login file" in text or "cookie.txt" in text
    finally:
        fake.stop()
        store.close()


def test_handle_url_sends_worker_file(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = _settings(tmp_path, fake.base_url)
        settings.data_dir.mkdir(parents=True)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)

        def runner(job_path: Path, timeout: int) -> None:
            spec = read_job(job_path)
            dest = spec.dest_dir / "forced.bin"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"ok")
            write_result(
                job_path,
                ResultSpec(
                    job_id=spec.job_id,
                    ok=True,
                    path=dest,
                    title="forced",
                    error=None,
                    result_path=job_path,
                ),
            )

        handle_url(
            api,
            settings,
            store,
            10,
            "https://example.com/v",
            runner=runner,
            message_id=88,
        )
        methods = [str(call["method"]) for call in fake.calls]
        assert "sendChatAction" in methods
        assert "sendRichMessageDraft" in methods
        assert "setMessageReaction" in methods
        assert "sendDocument" in methods
        assert "sendRichMessage" not in methods
        files_root = settings.data_dir / "files"
        leftovers = list(files_root.rglob("*")) if files_root.exists() else []
        assert leftovers == []
    finally:
        fake.stop()
        store.close()


def test_process_update_start() -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        with TemporaryDirectory() as raw:
            tmp_path = Path(raw)
            settings = _settings(tmp_path, fake.base_url)
            store = Store(settings.data_dir / "bot.sqlite")
            api = BotAPI(fake.token, fake.base_url, timeout=5)
            process_update(
                api,
                settings,
                store,
                {"message": {"chat": {"id": 3}, "text": "/start@mtrxdevbot"}},
            )
            store.close()
        assert fake.calls[-1]["method"] == "sendRichMessage"
    finally:
        fake.stop()
