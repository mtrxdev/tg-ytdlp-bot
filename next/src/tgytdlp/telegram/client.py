from pyrogram import Client

from tgytdlp.config import Settings


def build_client(settings: Settings) -> Client:
    return Client(
        name=settings.session_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token,
    )
