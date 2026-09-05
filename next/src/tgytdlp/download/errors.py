_BOT_CHECK = "confirm you"
_BOT_CHECK_TAIL = "not a bot"


def user_download_error(error: str | None) -> str:
    text = (error or "").strip()
    if not text:
        return "Download failed."
    lowered = text.lower()
    if _BOT_CHECK in lowered and _BOT_CHECK_TAIL in lowered:
        return (
            "YouTube asked you to sign in.\n\n"
            "Send me a YouTube login file (cookie.txt) as a document, "
            "then send this link again.\n\n"
            "Tap /cookies for the short how-to."
        )
    return text
