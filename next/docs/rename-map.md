# Old path to new path

Old tree stays the running bot until a slice is ported, tested, and shown in Telegram. New names drop ALLCAPS directories and `_cmd` / `_hlp` suffixes.

| Old | New |
|---|---|
| `magic.py` | `next/src/tgytdlp/__main__.py` |
| `HELPERS/app_instance.py` | gone. Pass `Client` in. No global app. |
| `CONFIG/_config.py` | `next/src/tgytdlp/config/__init__.py` (`Settings` from TOML + env) |
| `CONFIG/config.py` | `next/settings.toml` (gitignored) |
| `CONFIG/limits.py` | `next/src/tgytdlp/config/limits.py` |
| `CONFIG/domains.py` | `next/src/tgytdlp/config/domains.py` |
| `CONFIG/commands.py` | `next/src/tgytdlp/telegram/commands.py` |
| `CONFIG/messages.py` | `next/src/tgytdlp/i18n/messages.py` |
| `CONFIG/errors.py` | `next/src/tgytdlp/i18n/errors.py` |
| `CONFIG/logger_msg.py` | `next/src/tgytdlp/i18n/log_messages.py` |
| `CONFIG/LANGUAGES/language_router.py` | `next/src/tgytdlp/i18n/router.py` |
| `CONFIG/LANGUAGES/messages_XX.py` | `next/src/tgytdlp/i18n/locales/xx.py` |
| `COMMANDS/format_cmd.py` | `next/src/tgytdlp/telegram/handlers/format.py` |
| `COMMANDS/split_sizer.py` | `next/src/tgytdlp/telegram/handlers/split.py` |
| `COMMANDS/subtitles_cmd.py` | `next/src/tgytdlp/telegram/handlers/subtitles.py` |
| `COMMANDS/dubs_cmd.py` | `next/src/tgytdlp/telegram/handlers/dubs.py` |
| `COMMANDS/proxy_cmd.py` | `next/src/tgytdlp/telegram/handlers/proxy.py` |
| `COMMANDS/link_cmd.py` | `next/src/tgytdlp/telegram/handlers/link.py` |
| `COMMANDS/image_cmd.py` | `next/src/tgytdlp/telegram/handlers/image.py` |
| `COMMANDS/mediainfo_cmd.py` | `next/src/tgytdlp/telegram/handlers/mediainfo.py` |
| `COMMANDS/nsfw_cmd.py` | `next/src/tgytdlp/telegram/handlers/nsfw.py` |
| `COMMANDS/args_cmd.py` | `next/src/tgytdlp/telegram/handlers/args.py` |
| `COMMANDS/list_cmd.py` | `next/src/tgytdlp/telegram/handlers/sites.py` |
| `COMMANDS/tag_cmd.py` | `next/src/tgytdlp/telegram/handlers/tags.py` |
| `COMMANDS/search.py` | `next/src/tgytdlp/telegram/handlers/search.py` |
| `COMMANDS/clean_cmd.py` | `next/src/tgytdlp/telegram/handlers/clean.py` |
| `COMMANDS/cookies_cmd.py` | `next/src/tgytdlp/telegram/handlers/cookies.py` |
| `COMMANDS/lang_cmd.py` | `next/src/tgytdlp/telegram/handlers/lang.py` |
| `COMMANDS/keyboard_cmd.py` | `next/src/tgytdlp/telegram/handlers/keyboard.py` |
| `COMMANDS/settings_cmd.py` | `next/src/tgytdlp/telegram/handlers/settings.py` |
| `COMMANDS/admin_cmd.py` | `next/src/tgytdlp/telegram/handlers/admin.py` |
| `COMMANDS/other_handlers.py` | split into `audio.py`, `playlist.py`, `help.py` under handlers |
| `URL_PARSERS/url_extractor.py` | `next/src/tgytdlp/url/extract.py` plus per-command handlers |
| `URL_PARSERS/video_extractor.py` | `next/src/tgytdlp/url/video.py` |
| `URL_PARSERS/engine_router.py` | `next/src/tgytdlp/url/route.py` |
| `URL_PARSERS/youtube.py` | `next/src/tgytdlp/url/youtube.py` |
| `URL_PARSERS/filter_utils.py` | `next/src/tgytdlp/url/filters.py` |
| `URL_PARSERS/thumbnail_downloader.py` | `next/src/tgytdlp/download/thumbnail.py` |
| `URL_PARSERS/embedder.py` | `next/src/tgytdlp/url/embed.py` |
| `URL_PARSERS/nocookie.py` | `next/src/tgytdlp/url/nocookie.py` |
| `URL_PARSERS/service_api_info.py` | `next/src/tgytdlp/url/services.py` |
| `DOWN_AND_UP/yt_dlp_hook.py` | `next/src/tgytdlp/download/ytdlp.py` |
| `DOWN_AND_UP/gallery_dl_hook.py` | `next/src/tgytdlp/download/gallery.py` |
| `DOWN_AND_UP/down_and_up.py` | `next/src/tgytdlp/download/pipeline.py` |
| `DOWN_AND_UP/down_and_audio.py` | `next/src/tgytdlp/download/audio.py` |
| `DOWN_AND_UP/always_ask_menu.py` | `next/src/tgytdlp/download/format_menu.py` |
| `DOWN_AND_UP/sender.py` | `next/src/tgytdlp/download/send.py` |
| `DOWN_AND_UP/ffmpeg.py` | `next/src/tgytdlp/download/ffmpeg.py` |
| `DOWN_AND_UP/live_stream_downloader.py` | `next/src/tgytdlp/download/live.py` |
| `DATABASE/firebase_init.py` | `next/src/tgytdlp/store/firebase.py` |
| `DATABASE/cache_db.py` | `next/src/tgytdlp/store/cache.py` |
| `DATABASE/download_firebase.py` | `next/src/tgytdlp/store/remote_cache.py` |
| `HELPERS/logger.py` | `next/src/tgytdlp/log.py` |
| `HELPERS/limitter.py` | `next/src/tgytdlp/telegram/limits.py` |
| `HELPERS/channel_guard.py` | `next/src/tgytdlp/telegram/channel_guard.py` |
| `HELPERS/safe_messeger.py` | `next/src/tgytdlp/telegram/safe_send.py` |
| `HELPERS/fallback_helper.py` | `next/src/tgytdlp/download/fallback.py` |
| `HELPERS/pot_helper.py` | `next/src/tgytdlp/download/pot.py` |
| `HELPERS/proxy_helper.py` | `next/src/tgytdlp/download/proxy.py` |
| `HELPERS/porn.py` | `next/src/tgytdlp/download/nsfw.py` |
| `web/dashboard_app.py` | `next/src/tgytdlp/web/app.py` |
| `services/*.py` | `next/src/tgytdlp/web/` |
| `PATCH/GLOBAL_MESSAGES_PATCH.py` | gone. No import-time monkeypatch. |
| `scripts/docker-entrypoint.sh` | stays at repo root until Docker cutover |

Rows whose new file is not on disk yet are reserved. Port one row at a time. Test before the next row.
