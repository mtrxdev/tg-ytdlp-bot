# next

Rewrite of the bot in a new tree. The old ALLCAPS layout stays the production process until a slice is ported and proven.

Requires [Python 3.14.7](https://www.python.org/downloads/release/python-3147/). Settings follow that release's standard library: [tomllib](https://docs.python.org/3.14/library/tomllib.html) for the local file, [os.environ](https://docs.python.org/3.14/library/os.html#os.environ) to override, [argparse](https://docs.python.org/3.14/library/argparse.html) for flags (`suggest_on_error=True`), [logging](https://docs.python.org/3.14/howto/logging.html) for process events. Annotations use deferred evaluation from [PEP 649](https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-pep649). No `from __future__ import annotations`.

## Names

See [docs/tree.md](docs/tree.md) and [docs/rename-map.md](docs/rename-map.md). Files drop `_cmd`, `_hlp`, and shouty directories. One command, one handler module.

## Telegram keys

Do not paste `api_id`, `api_hash`, or `bot_token` in chat.

Use a dedicated BotFather test bot, not a bot that already has users.

```bash
cd next
cp settings.toml.example settings.toml
```

Fill `api_id`, `api_hash`, and `bot_token` in `next/settings.toml`. That file is gitignored. Process env `TG_API_ID`, `TG_API_HASH`, `TG_BOT_TOKEN`, and `TG_SESSION_NAME` override the file.

```bash
cd next
python3.14 -m venv .venv
source .venv/bin/activate
python --version   # Python 3.14.7
pip install -e ".[dev]"
pytest
python -m tgytdlp --check
python -m tgytdlp
```

`--check` starts the client, prints the username, and stops. The long-lived process answers `/start` in private chat.

## What is live now

Settings load from TOML and env. The client is built without a global app. `/start` replies. Download, cookies, i18n, and the dashboard are not ported yet.
