import logging
from typing import Optional

import httpx

from processors.adapters.error_tracking import write_warn_message
from processors.adapters.lock import async_lock
from processors.domain.logic import domain_from_url

logger = logging.getLogger(__name__)

# https://user-agents.net/browsers/firefox
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0)"
    " Gecko/20100101 Firefox/96.0"
)


@async_lock(key=lambda url, **_: domain_from_url(url))
async def fetch_text_from_url(url: str, *, encoding="") -> Optional[str]:
    # TODO don't fetch if content is not changed
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"user-agent": DEFAULT_UA})

        if encoding:
            res.encoding = encoding

        if res.status_code >= 400:
            write_warn_message(
                f"Can't fetch {url}: {res.status_code}. {res.text}"
            )
            return None

        return res.text
