from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from tgytdlp.telegram.api import BotAPI, BotAPIError
from tgytdlp.telegram.ids import ephemeral_id_from, is_private_chat, message_id_from
from tgytdlp.telegram.rich import dismiss_keyboard


@dataclass
class Status:
    chat_id: int
    message_id: int | None = None
    ephemeral_message_id: int | None = None
    receiver_user_id: int | None = None
    extra_ids: list[int] = field(default_factory=list)

    def edit(
        self,
        api: BotAPI,
        rich_message: Mapping[str, object],
        *,
        reply_markup: Mapping[str, object] | None = None,
    ) -> None:
        try:
            if (
                self.ephemeral_message_id is not None
                and self.receiver_user_id is not None
            ):
                api.edit_ephemeral_message_text(
                    self.chat_id,
                    self.receiver_user_id,
                    self.ephemeral_message_id,
                    rich_message=rich_message,
                    reply_markup=reply_markup,
                )
                return
            if self.message_id is not None:
                api.edit_message_text(
                    self.chat_id,
                    self.message_id,
                    rich_message=rich_message,
                    reply_markup=reply_markup,
                )
        except BotAPIError:
            return

    def dismiss(self, api: BotAPI, *, keep_user: bool = False) -> None:
        if (
            self.ephemeral_message_id is not None
            and self.receiver_user_id is not None
        ):
            try:
                api.delete_ephemeral_message(
                    self.chat_id,
                    self.receiver_user_id,
                    self.ephemeral_message_id,
                )
            except BotAPIError:
                pass
        ids: list[int] = []
        if self.message_id is not None:
            ids.append(self.message_id)
        if not keep_user:
            ids.extend(self.extra_ids)
        sweep_messages(api, self.chat_id, ids, private_only=False)


def sweep_messages(
    api: BotAPI,
    chat_id: int,
    message_ids: Sequence[int | None],
    *,
    private_only: bool,
) -> None:
    if private_only and not is_private_chat(chat_id):
        return
    ids = [item for item in message_ids if isinstance(item, int)]
    if not ids:
        return
    try:
        api.delete_messages(chat_id, ids)
        return
    except BotAPIError:
        pass
    for item in ids:
        try:
            api.delete_message(chat_id, item)
        except BotAPIError:
            continue


def status_from_send(
    chat_id: int,
    result: Mapping[str, object],
    *,
    receiver_user_id: int | None = None,
    extra_ids: Sequence[int | None] = (),
) -> Status:
    extras = [item for item in extra_ids if isinstance(item, int)]
    return Status(
        chat_id=chat_id,
        message_id=message_id_from(result),
        ephemeral_message_id=ephemeral_id_from(result),
        receiver_user_id=receiver_user_id,
        extra_ids=extras,
    )


def send_status(
    api: BotAPI,
    chat_id: int,
    rich_message: Mapping[str, object],
    *,
    user_id: int | None = None,
    query_id: str | None = None,
    replace_callback: bool = False,
    reply_to: int | None = None,
    extra_ids: Sequence[int | None] = (),
    dismissable: bool = False,
    reply_markup: Mapping[str, object] | None = None,
) -> Status:
    ephemeral: dict[str, object] | None = None
    if user_id is not None and not is_private_chat(chat_id):
        ephemeral = {"receiver_user_id": user_id}
        if query_id:
            ephemeral["callback_query_id"] = query_id
            if replace_callback:
                ephemeral["replace_callback_query_message"] = True
    markup = reply_markup
    if dismissable and markup is None:
        markup = dismiss_keyboard()
    reply: dict[str, object] | None = None
    if reply_to is not None:
        reply = {"message_id": reply_to}
    result = api.send_rich_message(
        chat_id,
        rich_message,
        reply_markup=markup,
        ephemeral_message_parameters=ephemeral,
        reply_parameters=reply,
    )
    return status_from_send(
        chat_id,
        result,
        receiver_user_id=user_id if ephemeral is not None else None,
        extra_ids=extra_ids,
    )
