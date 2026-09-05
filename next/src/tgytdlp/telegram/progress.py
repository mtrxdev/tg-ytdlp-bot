from __future__ import annotations

import threading
from collections.abc import Callable
from urllib.parse import urlparse

from tgytdlp.telegram.api import BotAPI, BotAPIError
from tgytdlp.telegram.ids import is_private_chat
from tgytdlp.telegram.rich import dismiss_keyboard, draft_rich, progress_rich
from tgytdlp.telegram.status import send_status

REACT_WAIT = "👀"
REACT_OK = "👍"
REACT_FAIL = "👎"
CHAT_ACTION = "upload_document"
PULSE_SECONDS = 4.0


def draft_id_for(job_id: str) -> int:
    try:
        value = int(job_id[:8], 16) % 2_000_000_000
    except ValueError:
        value = 1
    return value or 1


def host_of(url: str) -> str:
    host = urlparse(url).hostname
    if not host:
        return "the link"
    if host.startswith("www."):
        host = host[4:]
    return host


def wait_for_worker(run: Callable[[], None], pulse: Callable[[], None]) -> None:
    done = threading.Event()
    errors: list[BaseException] = []

    def target() -> None:
        try:
            run()
        except BaseException as exc:
            errors.append(exc)
        finally:
            done.set()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    while not done.wait(PULSE_SECONDS):
        pulse()
    thread.join()
    if errors:
        raise errors[0]


class JobLive:
    def __init__(
        self,
        api: BotAPI,
        chat_id: int,
        job_id: str,
        url: str,
        *,
        message_id: int | None = None,
        user_id: int | None = None,
    ) -> None:
        self._api = api
        self.chat_id = chat_id
        self.job_id = job_id
        self.url = url
        self.message_id = message_id
        self.user_id = user_id
        self.draft_id = draft_id_for(job_id)
        self.step = 0
        self._private = is_private_chat(chat_id)

    def start(self) -> None:
        self._react(REACT_WAIT)
        self.pulse()

    def pulse(self) -> None:
        try:
            self._api.send_chat_action(self.chat_id, CHAT_ACTION)
        except BotAPIError:
            pass
        if not self._private:
            return
        try:
            self._api.send_rich_message_draft(
                self.chat_id,
                self.draft_id,
                draft_rich(self.step, host=host_of(self.url)),
            )
        except BotAPIError:
            pass

    def set_step(self, step: int) -> None:
        self.step = step
        self.pulse()

    def fail(self, title: str, body: str) -> None:
        self._react(REACT_FAIL)
        send_status(
            self._api,
            self.chat_id,
            progress_rich(title, body),
            user_id=self.user_id,
            dismissable=True,
            reply_markup=dismiss_keyboard(),
            reply_to=self.message_id,
        )

    def succeed(self) -> None:
        self._react(REACT_OK)

    def _react(self, emoji: str) -> None:
        if self.message_id is None:
            return
        try:
            self._api.set_message_reaction(self.chat_id, self.message_id, emoji)
        except BotAPIError:
            pass
