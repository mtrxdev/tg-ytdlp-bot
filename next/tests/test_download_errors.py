from tgytdlp.download.errors import user_download_error


def test_user_download_error_maps_youtube_bot_check() -> None:
    raw = (
        "ERROR: [youtube] t1BWMa8btIw: Sign in to confirm you’re not a bot. "
        "Use --cookies-from-browser or --cookies for the authentication."
    )
    message = user_download_error(raw)
    assert "TG_COOKIES" in message
    assert "4416" in message
    assert "t1BWMa8btIw" not in message


def test_user_download_error_keeps_other_text() -> None:
    assert user_download_error("no such file") == "no such file"
    assert user_download_error(None) == "Download failed."
    assert user_download_error("") == "Download failed."
