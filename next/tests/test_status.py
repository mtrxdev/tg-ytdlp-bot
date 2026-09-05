from pathlib import Path

from tgytdlp.config import settings_from_mapping
from tgytdlp.jobs.files import ResultSpec, read_job, write_result
from tgytdlp.store.sqlite import Store
from tgytdlp.telegram.api import BotAPI
from tgytdlp.telegram.handlers import process_update
from tgytdlp.telegram.handlers.urls import handle_url
from tgytdlp.telegram.rich import how_rich, start_rich
from tgytdlp.telegram.status import Status, send_status
from tests.support.botapi import FakeBotAPI
from tests.support.rich import flatten_rich


def test_start_rich_has_heading() -> None:
    rich = start_rich("paste a link")
    assert flatten_rich(rich).startswith("Send a link")
    assert "paste a link" in flatten_rich(rich)


def test_status_edit_and_dismiss(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        status = send_status(api, 10, how_rich("steps"), extra_ids=[7], dismissable=True)
        assert status.message_id == 1
        status.edit(api, how_rich("updated"))
        status.dismiss(api)
        methods = [str(call["method"]) for call in fake.calls]
        assert methods[0] == "sendRichMessage"
        assert "editMessageText" in methods
        assert "deleteMessages" in methods
        delete = next(call for call in fake.calls if call["method"] == "deleteMessages")
        body = delete["body"]
        assert isinstance(body, dict)
        assert body["message_ids"] == [1, 7]
    finally:
        fake.stop()


def test_dismiss_callback_deletes(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = settings_from_mapping(
            {
                "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
                "TG_API_BASE": fake.base_url,
                "TG_DATA_DIR": str(tmp_path / "data"),
                "TG_POLL_TIMEOUT": "1",
            },
            relative_to=tmp_path,
        )
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)
        process_update(
            api,
            settings,
            store,
            {
                "callback_query": {
                    "id": "cb-dismiss",
                    "data": "dismiss",
                    "from": {"id": 5},
                    "message": {"chat": {"id": 10}, "message_id": 44},
                }
            },
        )
        methods = [str(call["method"]) for call in fake.calls]
        assert "deleteMessages" in methods
        store.close()
    finally:
        fake.stop()


def test_failed_url_edits_status_and_cleans(tmp_path: Path) -> None:
    fake = FakeBotAPI("1234567890:AAExampleTokenValue_12-xx")
    fake.start()
    try:
        settings = settings_from_mapping(
            {
                "TG_BOT_TOKEN": "1234567890:AAExampleTokenValue_12-xx",
                "TG_API_BASE": fake.base_url,
                "TG_DATA_DIR": str(tmp_path / "data"),
                "TG_POLL_TIMEOUT": "1",
            },
            relative_to=tmp_path,
        )
        settings.data_dir.mkdir(parents=True)
        store = Store(settings.data_dir / "bot.sqlite")
        api = BotAPI(fake.token, fake.base_url, timeout=5)

        def runner(job_path: Path, timeout: int) -> None:
            spec = read_job(job_path)
            spec.dest_dir.mkdir(parents=True, exist_ok=True)
            (spec.dest_dir / "partial.bin").write_bytes(b"x")
            write_result(
                job_path,
                ResultSpec(
                    job_id=spec.job_id,
                    ok=False,
                    path=None,
                    title=None,
                    error="Sign in to confirm you’re not a bot.",
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
            message_id=99,
        )
        methods = [str(call["method"]) for call in fake.calls]
        assert "sendChatAction" in methods
        assert "sendRichMessageDraft" in methods
        assert "setMessageReaction" in methods
        assert "sendRichMessage" in methods
        assert "editMessageText" not in methods
        assert "sendDocument" not in methods
        rich_sends = [
            call for call in fake.calls if call["method"] == "sendRichMessage"
        ]
        assert len(rich_sends) == 1
        body = rich_sends[0]["body"]
        assert isinstance(body, dict)
        rich = body["rich_message"]
        assert isinstance(rich, dict)
        assert flatten_rich(rich).startswith("Could not download")
        files_root = settings.data_dir / "files"
        leftovers = list(files_root.rglob("*")) if files_root.exists() else []
        assert leftovers == []
        store.close()
    finally:
        fake.stop()


def test_status_dataclass_defaults() -> None:
    status = Status(chat_id=1)
    assert status.message_id is None
    assert status.extra_ids == []
