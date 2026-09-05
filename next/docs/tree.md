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
      ids.py                 # chat / message / ephemeral ids
      rich.py                # InputRichMessage blocks
      status.py              # help / error overlay: send, edit, delete
      progress.py            # chat action + rich draft + reaction
      handlers/
        start.py             # /start + inline keyboard
        callbacks.py
        cookies.py           # /cookies, document cookie.txt, /save_as_cookie
        urls.py
    cookies/                 # Netscape validate + per-chat cookie.txt
    jobs/                    # JSON job files + subprocess argv
      cleanup.py             # dest dir + job JSON after send
    store/sqlite.py          # offset + job index
    download/send.py         # sendDocument (no yt_dlp)
    download/errors.py       # user-facing worker errors (no yt_dlp)
    worker/                  # separate process; embeds YoutubeDL
      opts.py                # Node JS runtime + optional cookiefile
  tests/
```

Reserved empty packages (`url/`, `i18n/`, `web/`) stay unused until a later slice.
