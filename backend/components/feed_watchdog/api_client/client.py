import asyncio
import logging
from functools import wraps
from typing import AsyncGenerator

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


class FeedWatchdogAPIClientError(Exception):
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

    async def get_streams(
        self, interval: str | None = None
    ) -> list[StreamResp]:
        result: list[StreamResp] = []
        params = {"only_active": True}
        if interval is not None:
            params["interval"] = interval
        async for row in self._iterate_pagination(path="/streams/", **params):
            result.append(StreamResp.parse_obj(row))
        return result

    async def get_stream(self, slug: str) -> StreamResp | None:
        async for row in self._iterate_pagination(
            path="/streams/", q=slug, page_size=10
        ):
            stream = StreamResp.parse_obj(row)
            if stream.slug == slug:
                return stream
        return None

    async def _iterate_pagination(
        self, path: str, page=1, page_size=300, **kwargs
    ) -> AsyncGenerator[dict, None]:
        has_next = True
        while has_next:
            try:
                response = await self._client.get(
                    f"{self._base_url}{path}",
                    params={
                        "page": page,
                        "page_size": page_size + 1,
                        **kwargs,
                    },
                )
                response.raise_for_status()
                result = response.json()
                has_next = len(result["results"]) == page_size + 1
                for row in result["results"]:
                    yield row
            except httpx.HTTPError as e:
                raise FeedWatchdogAPIClientError(
                    "Error while fetching streams"
                ) from e
            page += 1

    @infinite_retry
    async def get_intervals(self) -> list[str]:
        response = await self._client.get(
            f"{self._base_url}/streams/intervals/"
        )
        response.raise_for_status()
        return [item["value"] for item in response.json()]
