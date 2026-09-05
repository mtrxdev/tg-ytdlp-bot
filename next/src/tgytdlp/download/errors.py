_BOT_CHECK = "confirm you"
_BOT_CHECK_TAIL = "not a bot"


def user_download_error(error: str | None) -> str:
    text = (error or "").strip()
    if not text:
        return "Download failed."
    lowered = text.lower()
    if _BOT_CHECK in lowered and _BOT_CHECK_TAIL in lowered:
        return (
            "YouTube asked for sign-in (bot check). "
            "Public videos need Node + yt-dlp-ejs and the PO-token provider "
            "on 127.0.0.1:4416. Age-restricted or locked videos need a "
            "Netscape cookies file in TG_COOKIES."
        )
    return text
