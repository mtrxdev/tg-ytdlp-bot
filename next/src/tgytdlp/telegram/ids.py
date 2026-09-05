from collections.abc import Mapping


def as_mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {str(key): item for key, item in value.items()}


def int_field(data: Mapping[str, object], name: str) -> int | None:
    raw = data.get(name)
    return raw if isinstance(raw, int) else None


def user_id_from(data: Mapping[str, object]) -> int | None:
    sender = as_mapping(data.get("from"))
    if sender is None:
        return None
    return int_field(sender, "id")


def chat_id_from_message(message: Mapping[str, object]) -> int | None:
    chat = as_mapping(message.get("chat"))
    if chat is None:
        return None
    return int_field(chat, "id")


def message_id_from(data: Mapping[str, object]) -> int | None:
    return int_field(data, "message_id")


def ephemeral_id_from(data: Mapping[str, object]) -> int | None:
    return int_field(data, "ephemeral_message_id")


def is_private_chat(chat_id: int) -> bool:
    return chat_id > 0
