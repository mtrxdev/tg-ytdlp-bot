# next

Greenfield rewrite. Official [Bot API 10.3](https://core.telegram.org/bots/api) over HTTPS, CPython 3.14.7, yt-dlp in a **separate worker process**. The chat process never imports `yt_dlp`.

**New chat:** read [docs/handoff.md](docs/handoff.md) and [AGENTS.md](AGENTS.md) first.

The old ALLCAPS tree stays the production bot until this rewrite is proven.

## Secrets — do not put the token in a GitHub file

A BotFather token in a tracked file (`settings.toml`, `.env`, `config.py`) is copied into git history the moment you commit or edit it on github.com. Do not do that.

**Where to put `TG_BOT_TOKEN`:**

1. **This cloud agent:** Cursor environment / agent secret named `TG_BOT_TOKEN`. After it is saved, send another message so the VM can see it.
2. **GitHub Actions only:** repo **Settings → Secrets and variables → Actions → New repository secret**, name `TG_BOT_TOKEN`. That secret is not a file and is not available in this coding VM.
3. **Your machine:** copy `settings.toml.example` to `settings.toml` (gitignored) and fill `bot_token`.

`api_id` / `api_hash` belong on the local `telegram-bot-api` server binary, not in the bot process.

## Run

Requires [Python 3.14.7](https://www.python.org/downloads/release/python-3147/).

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

`--check` calls official `getMe` and prints `@username`. The long-lived process long-polls `getUpdates`. `/start` sends an inline keyboard. A public URL runs `python -m tgytdlp.worker`. Files go out via `sendDocument` (multipart on `api.telegram.org`, `file://` on a local Bot API server).
