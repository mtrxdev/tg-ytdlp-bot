# next/ tree

```
next/
  pyproject.toml
  settings.toml.example      # not the secret; copy locally
  src/tgytdlp/
    __main__.py              # chat process: getMe / getUpdates
    config/                  # tomllib + os.environ (token only)
    telegram/
      api.py                 # thin Bot API 10.3 client (requests)
      client.py              # build_api factory
      poll.py                # getUpdates long poll
      handlers/
        start.py             # /start + inline keyboard
        callbacks.py
        urls.py
    jobs/                    # JSON job files + subprocess argv
    store/sqlite.py          # offset + job index
    download/send.py         # sendDocument (no yt_dlp)
    worker/                  # separate process; embeds YoutubeDL
  tests/
```

Reserved empty packages (`url/`, `i18n/`, `web/`) stay unused until a later slice.
