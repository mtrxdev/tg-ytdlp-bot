_BOT_CHECK = "confirm you"
_BOT_CHECK_TAIL = "not a bot"
_YOUTUBE_SIGNIN = (
    "YouTube asked you to sign in.\n\n"
    "Send me a YouTube login file (cookie.txt) as a document, "
    "then send this link again.\n\n"
    "Tap /cookies for the short how-to."
)
_SITE_BLOCKED = "This site blocked the download. Try another public URL."
_GENERIC_FAIL = (
    "I could not fetch that link. Try another public URL, "
    "or send a YouTube login file if YouTube asked you to sign in."
)


def user_download_error(error: str | None) -> str:
    text = (error or "").strip()
    if not text:
        return "Download failed."
    lowered = text.lower()
    if _BOT_CHECK in lowered and _BOT_CHECK_TAIL in lowered:
        return _YOUTUBE_SIGNIN
    if (
        "cloudflare" in lowered
        or "anti-bot" in lowered
        or "http error 403" in lowered
        or "impersonat" in lowered
    ):
        return _SITE_BLOCKED
    return _GENERIC_FAIL
