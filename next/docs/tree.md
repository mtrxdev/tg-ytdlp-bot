# next/ tree

Domain packages, not ALLCAPS leftovers. Empty packages are reserved homes from [rename-map.md](rename-map.md). Do not put logic in them until that slice is ported and tested.

```
next/
  pyproject.toml
  .env.example
  docs/
    tree.md
    rename-map.md
  src/tgytdlp/
    __main__.py              process entry (was magic.py)
    config/                  env-parsed Settings (was CONFIG/)
    telegram/
      client.py              Client factory
      handlers/              one module per command, no _cmd suffix
        start.py
    download/                reserved: yt-dlp / gallery-dl / ffmpeg / send
    url/                     reserved: URL parse and engine route
    store/                   reserved: cache and firebase
    i18n/                    reserved: language packs
    web/                     reserved: dashboard
  tests/
```

Secrets live in `next/.env`, never in a Python class, never in chat.
