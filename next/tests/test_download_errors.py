from tgytdlp.download.errors import user_download_error


def test_user_download_error_maps_youtube_bot_check() -> None:
    raw = (
        "ERROR: [youtube] t1BWMa8btIw: Sign in to confirm you’re not a bot. "
        "Use --cookies-from-browser or --cookies for the authentication."
    )
    message = user_download_error(raw)
    assert "/cookies" in message
    assert "cookie.txt" in message
    assert "TG_COOKIES" not in message
    assert "t1BWMa8btIw" not in message


def test_user_download_error_keeps_other_text() -> None:
    assert user_download_error("no such file") == "no such file"
    assert user_download_error(None) == "Download failed."
    assert user_download_error("") == "Download failed."


def test_user_download_error_hides_ytdlp_cli() -> None:
    raw = (
        "ERROR: [generic] Got HTTP Error 403 caused by Cloudflare anti-bot "
        "challenge; see https://github.com/yt-dlp/yt-dlp#impersonation "
        'for how to install the required impersonation dependency, and try '
        'again with --extractor-args "generic:impersonate"'
    )
    message = user_download_error(raw)
    assert "Cloudflare" not in message
    assert "ERROR:" not in message
    assert "--extractor-args" not in message
    assert "blocked" in message.lower()
