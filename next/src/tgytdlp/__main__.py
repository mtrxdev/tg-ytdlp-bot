from __future__ import annotations

import sys

from pyrogram import idle

from tgytdlp.config import SettingsError, load_settings
from tgytdlp.telegram import build_client, register_all


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        settings = load_settings()
    except SettingsError as exc:
        print(exc, file=sys.stderr)
        return 2

    app = build_client(settings)
    check_only = args == ["--check"]
    if not check_only:
        register_all(app)

    app.start()
    try:
        me = app.get_me()
        label = me.username or str(me.id)
        print(f"connected @{label}" if me.username else f"connected {label}")
        if check_only:
            return 0
        idle()
    finally:
        app.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
