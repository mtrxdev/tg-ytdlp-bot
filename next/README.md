# next

Rewrite of the bot in a new tree. The old ALLCAPS layout stays the production process until a slice is ported and proven.

## Names

See [docs/tree.md](docs/tree.md) and [docs/rename-map.md](docs/rename-map.md). Files drop `_cmd`, `_hlp`, and shouty directories. One command, one handler module.

## Telegram keys

Do not paste `API_ID`, `API_HASH`, or `BOT_TOKEN` in chat.

Use a dedicated BotFather test bot, not a bot that already has users.

```bash
cd next
cp .env.example .env
```

Fill `TG_API_ID`, `TG_API_HASH`, `TG_BOT_TOKEN` in `next/.env`. That file is gitignored.

```bash
cd next
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m tgytdlp --check
python -m tgytdlp
```

`--check` starts the client, prints the username, and stops. The long-lived process answers `/start` in private chat.

## What is live now

Settings load from env. The client is built without a global app. `/start` replies. Download, cookies, i18n, and the dashboard are not ported yet.
