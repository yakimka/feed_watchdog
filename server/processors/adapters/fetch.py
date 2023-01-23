import asyncio
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
async def fetch_text_from_url(
    url: str, *, encoding="", retry=0
) -> Optional[str]:
    # TODO don't fetch if content is not changed
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        while True:
            try:
                res = await client.get(
                    url, headers={"user-agent": DEFAULT_UA}, timeout=30.0
                )
                res.raise_for_status()
            except httpx.HTTPError as e:
                if retry > 0:
                    logger.warning(
                        "Failed to fetch %s with %s and %s retries left."
                        " Retrying...",
                        url,
                        e,
                        retry,
                    )
                    retry -= 1
                    await asyncio.sleep(3.0)
                    continue

                write_warn_message(
                    f"Error while fetching {url}: error"
                    f" {type(e).__name__}\n{e}",
                    logger=logger,
                )
                return None

            if encoding:
                res.encoding = encoding

            return res.text
