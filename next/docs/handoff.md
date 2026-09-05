# Handoff — pick up here

Read this file first in a new chat. Then read [README.md](../README.md), [tree.md](tree.md), and [rename-map.md](rename-map.md). Do not treat the old ALLCAPS tree as the destination.

## Where the work lives

| Item | Value |
|---|---|
| Repo | https://github.com/mtrxdev/tg-ytdlp-bot |
| Branch | `cursor/next-tree-rename-289c` |
| PR | https://github.com/mtrxdev/tg-ytdlp-bot/pull/1 |
| Base | `main` |
| Rewrite root | `next/` |
| Production bot | repo root (`magic.py`, `COMMANDS/`, …). Leave it running until `next/` is proven. |
| Test bot username | `@mtrxdevbot` |
| Cursor environment | https://cursor.com/dashboard/cloud-agents/environments/e/56af7e6c-a8f1-11f1-b532-320a589b8025 |

Latest rewrite commit on this branch: official Bot API client, isolated yt-dlp worker.

## Product decision

Greenfield rewrite. Old chelaxian/tg-ytdlp-bot code is **reference for behavior only**, not architecture. User asked for a better production-grade version from official Telegram and CPython docs.

## Approved stack (do not regress)

- CPython **3.14.7** for chat and worker. Pin in `next/.python-version` and `requires-python`.
- Official **Bot API 10.3** HTTPS JSON. Thin client we own (`requests`). No Pyrogram, Telethon, aiogram, python-telegram-bot.
- Bot process credential: **BotFather token only**. `api_id` / `api_hash` only for the official local `telegram-bot-api` **server binary**.
- Updates: `getUpdates` long poll (`timeout > 0`). Webhook later only if we leave one host.
- UI: `InlineKeyboardMarkup` + `answerCallbackQuery` first. Rich Messages later. Mini Apps later.
- Chat process **never** `import yt_dlp`. Worker is `python -m tgytdlp.worker --job <file>`.
- Worker embeds official `YoutubeDL`. ffmpeg is yt-dlp’s child. Never `communicate()` a multi-GB body.
- Jobs: atomic JSON under `data/jobs/` plus `sqlite3` WAL for offset and job index. No Redis/Celery/Firebase in v1.
- Files: `sendDocument` multipart on `https://api.telegram.org` (50 MB cap). `file://` URI when `api_base` is not `api.telegram.org` (local Bot API, 2000 MB).
- Config: `tomllib` + `os.environ` + `argparse` (`suggest_on_error=True`) + `logging`. No dotenv. `Settings.__repr__` redacts the token.
- gallery-dl is not core. Optional later worker.

Rejected: raw TDLib/MTProto in our process, Rust as the Telegram edge, one PID that imports yt-dlp, webhook/Mini App first.

## What already works (tested)

`cd next && python3.14 -m pytest -q` → **52 passed** (2026-09-05) against a fake Bot API HTTP server. Live `--check` printed `@mtrxdevbot`.

Implemented:

- Token-only settings (`TG_BOT_TOKEN`, `TG_API_BASE`, `TG_DATA_DIR`, timeouts)
- `BotAPI` in `src/tgytdlp/telegram/api.py`
- `--check` → official `getMe`, prints `@username`
- Long-poll loop, `/start` inline keyboard (`how`, `cookies`, `sample`)
- URL → job JSON → subprocess worker
- Isolation tests: chat sources must not import `yt_dlp`
- `sendDocument` file URI and multipart
- YouTube: worker sets `js_runtimes=node`; deps are `yt-dlp[default]` (EJS) and `bgutil-ytdlp-pot-provider`. Public extracts need the POT HTTP server on `127.0.0.1:4416`. Locked videos: user sends Netscape `cookie.txt` as a Telegram document (or `/save_as_cookie`). Stored at `data/users/<chat_id>/cookie.txt`. Operator `TG_COOKIES` is fallback only. Mini App Google login cannot supply those cookies.

## Live Telegram

Live `getMe` from a cloud agent printed `@mtrxdevbot` (2026-09-05). `TG_BOT_TOKEN` is a Cursor **environment** secret (not a GitHub Actions secret and not a repo file). `gh` cannot read secret values.

A later agent VM may not have CPython 3.14.7 on PATH. Install if missing (`uv python install 3.14.7` or official tarball `altinstall`), then recreate `next/.venv`.

To continue the live test:

1. Confirm `TG_BOT_TOKEN` is in `os.environ` (check length only; do not print).
2. `cd next && python -m tgytdlp --check` must print `@mtrxdevbot`.
3. `python -m tgytdlp` (tmux), then the user sends `/start` in Telegram.

Never paste the token in chat. Never commit `next/settings.toml`. Never log the token or the full `.../bot<token>/...` URL.

## First commands for the next agent

```bash
cd next
python3.14 --version    # 3.14.7; install if missing
python3.14 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m tgytdlp --check   # must print @mtrxdevbot
```

If `--check` prints `@mtrxdevbot`, start the poller (tmux) if it is not already running and ask the user to tap `/start`.

## After live /start works

1. Local official `telegram-bot-api --local` for files over 50 MB.
2. Port old capabilities one rename-map row at a time. Test each row. Do not dump ALLCAPS files into `next/`.
3. Keep production `magic.py` until cutover.

## Constraints the user set

- Official docs over convenience (https://docs.python.org/3.14/ and https://core.telegram.org/bots/api).
- New names, OCD tree, not in-place rename of production.
- Dedicated test bot, not a bot with users.
- Poteto-mode / brainstorming: no slop, no secrets in chat.

## Doc index

- [../README.md](../README.md) — run + secrets policy
- [tree.md](tree.md) — package map
- [rename-map.md](rename-map.md) — old ALLCAPS → new paths (most rows reserved)
- [../settings.toml.example](../settings.toml.example) — template only
