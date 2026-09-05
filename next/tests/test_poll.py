from pathlib import Path

from tgytdlp.config import settings_from_mapping
from tgytdlp.jobs.files import ResultSpec, write_result
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers import process_update
from tgytdlp.telegram.handlers.urls import handle_url
from tgytdlp.telegram.poll import poll_once
from tests.support.botapi import FakeBotAPI


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
        methods = [str(call["method"]) for call in fake.calls]
        assert "sendMessage" in methods
        assert "answerCallbackQuery" in methods
        assert "sendDocument" in methods
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
            dest = settings.data_dir / "files" / "forced.bin"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"ok")
            write_result(
                job_path,
                ResultSpec(
                    job_id="x",
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
        )
        methods = [str(call["method"]) for call in fake.calls]
        assert "sendChatAction" in methods
        assert "sendDocument" in methods
    finally:
        fake.stop()
        store.close()


def test_process_update_start() -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        from tempfile import TemporaryDirectory

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
        assert fake.calls[-1]["method"] == "sendMessage"
    finally:
        fake.stop()
