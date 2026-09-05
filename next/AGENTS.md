# Agent memory (`next/`)

New chat: start at [docs/handoff.md](docs/handoff.md).

- Rewrite lives in `next/`. Production bot is the old ALLCAPS tree. Do not replace `magic.py` until `next/` talks to Telegram and sends a file.
- Stack is frozen unless the user revises it: CPython 3.14.7, Bot API 10.3 + `requests`, token only, isolated yt-dlp worker, sqlite + job JSON, `sendDocument` (`file://` on local Bot API). Local/VPS: `getUpdates`. Vercel 24/7: HTTPS webhook on `api/index.py` (`POST /`); disk and cookies are ephemeral (`/tmp`).
- Chat process must never import `yt_dlp`. Tests in `tests/test_isolation.py` enforce this.
- Never commit `next/settings.toml`. Never paste `TG_BOT_TOKEN` in chat. GitHub Actions secrets are not visible to Cursor cloud VMs.
- Test bot username: `@mtrxdevbot`. Live `getMe` from an agent printed `@mtrxdevbot` (2026-09-05).
- Official docs only for Telegram and CPython 3.14. YouTube: Node + yt-dlp-ejs + bgutil POT on :4416. Locked videos: user sends `cookie.txt` in chat (`data/users/<chat_id>/`); `TG_COOKIES` is operator fallback only.
