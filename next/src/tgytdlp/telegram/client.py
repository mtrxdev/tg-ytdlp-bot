from tgytdlp.config import Settings
from tgytdlp.telegram.api import BotAPI, build_api

__all__ = ["BotAPI", "build_api"]


def build_client(settings: Settings) -> BotAPI:
    return build_api(settings)
