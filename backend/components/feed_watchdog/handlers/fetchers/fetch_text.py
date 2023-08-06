import dataclasses
import logging

from feed_watchdog.handlers import HandlerOptions, HandlerType, register_handler
from feed_watchdog.http import domain_from_url, fetch_text_from_url
from feed_watchdog.synchronize.lock import async_lock

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class FetchTextOptions(HandlerOptions):
    DESCRIPTIONS = {
        "url": ("URL", ""),
        "encoding": ("Page encoding", ""),
    }

    url: str
    encoding: str = ""


@async_lock(key=lambda options: domain_from_url(options.url))
@register_handler(type=HandlerType.fetchers.value, options=FetchTextOptions)
async def fetch_text(*, options: FetchTextOptions) -> str | None:
    return await fetch_text_from_url(
        options.url, encoding=options.encoding, retry=2
    )
