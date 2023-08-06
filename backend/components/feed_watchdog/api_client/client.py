import asyncio
import logging
from functools import wraps

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SourceResp(BaseModel):
    name: str
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str
    tags: list


class ReceiverResp(BaseModel):
    name: str
    slug: str
    type: str
    options: dict
    options_allowed_to_override: list[str]


class ModifierResp(BaseModel):
    type: str
    options: dict


class StreamResp(BaseModel):
    slug: str
    intervals: list[str]
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[ModifierResp]
    active: bool
    source: SourceResp
    receiver: ReceiverResp


class StreamClientError(Exception):
    pass


def infinite_retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        counter = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPError:
                counter += 1
                if counter == 10:
                    logger.exception("Too many retries")
                logger.info("%s retrying in 60 seconds", func.__name__)
                await asyncio.sleep(60)

    return wrapper


class FeedWatchdogAPIClient:
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url.removesuffix("/")

    async def get_streams(self, interval: str) -> list[StreamResp]:
        result: list[StreamResp] = []
        has_next = True
        page = 1
        while has_next:
            try:
                has_next, streams = await self._get_streams(
                    interval=interval, page=page
                )
            except httpx.HTTPError as e:
                raise StreamClientError("Error while fetching streams") from e
            page += 1
            result.extend(streams)
        return result

    async def _get_streams(
        self, interval: str, page=1, page_size=300
    ) -> tuple[bool, list[StreamResp]]:
        response = await self._client.get(
            f"{self._base_url}/streams/",
            params={
                "only_active": True,
                "page": page,
                "page_size": page_size,
                "interval": interval,
            },
        )
        response.raise_for_status()
        result = response.json()
        has_next = result["count"] > page * page_size
        return has_next, [
            StreamResp.parse_obj(stream) for stream in result["results"]
        ]

    @infinite_retry
    async def get_intervals(self) -> list[str]:
        response = await self._client.get(
            f"{self._base_url}/streams/intervals/"
        )
        response.raise_for_status()
        return [item["value"] for item in response.json()]
