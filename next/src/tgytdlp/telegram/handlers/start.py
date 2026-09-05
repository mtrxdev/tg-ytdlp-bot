from pyrogram import Client, filters
from pyrogram.types import Message


async def on_start(client: Client, message: Message) -> None:
    me = await client.get_me()
    name = me.username or "tgytdlp"
    await message.reply_text(f"{name} rewrite is up. Send a URL once download lands.")


def register_start(app: Client) -> None:
    app.on_message(filters.command("start") & filters.private)(on_start)
