from typing import Any, AsyncGenerator, Callable

import httpx
from picodi import Provide, inject, resource
from redis import asyncio as aioredis

from feed_watchdog.api_client.client import FeedWatchdogAPIClient
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.post import RedisPostRepository
from feed_watchdog.workers.settings import Settings, get_settings


@inject
def get_option(
    path: str, settings: Settings = Provide(get_settings)
) -> Callable[[], Any]:
    path_parts = path.split(".")
    if not path_parts:
        raise ValueError("Empty path")
    value = settings
    for part in path_parts:
        value = getattr(value, part)
    return lambda: value


@inject
def get_httpx_stream_client(
    token: str = Provide(get_option("app.api_token")),
    timeout: int = Provide(get_option("app.api_timeout")),
) -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(retries=2)
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(headers=headers, transport=transport, timeout=timeout)


@resource
@inject
async def get_storage_redis_client(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(url=settings.redis.storage_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()  # type: ignore[attr-defined]


@resource
@inject
async def get_pub_sub_redis_client(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(url=settings.redis.storage_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()  # type: ignore[attr-defined]


@inject
def get_publisher(
    redis: aioredis.Redis = Provide(get_pub_sub_redis_client),
) -> Publisher:
    return Publisher(redis_client=redis)


@inject
def get_feed_watchdog_api_client(
    client: httpx.AsyncClient = Provide(get_httpx_stream_client),
    base_url: str = Provide(get_option("app.api_base_url")),
) -> FeedWatchdogAPIClient:
    return FeedWatchdogAPIClient(client=client, base_url=base_url)


@inject
def get_post_repository(
    redis: aioredis.Redis = Provide(get_storage_redis_client),
) -> RedisPostRepository:
    return RedisPostRepository(client=redis)
