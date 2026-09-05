from pyrogram import Client

from tgytdlp.telegram.handlers.start import register_start


def register_all(app: Client) -> None:
    register_start(app)
