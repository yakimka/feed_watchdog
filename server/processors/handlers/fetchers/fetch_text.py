import dataclasses
import logging

from processors.adapters.fetch import fetch_text_from_url
from processors.handlers import HandlerOptions, HandlerType, register_handler

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class FetchTextOptions(HandlerOptions):
    DESCRIPTIONS = {
        "url": ("URL", ""),
        "encoding": ("Page encoding", ""),
    }

    url: str
    encoding: str = ""


@register_handler(type=HandlerType.fetchers.value, options=FetchTextOptions)
async def fetch_text(*, options: FetchTextOptions = None) -> str | None:
    return await fetch_text_from_url(
        options.url, encoding=options.encoding, retry=2
    )
