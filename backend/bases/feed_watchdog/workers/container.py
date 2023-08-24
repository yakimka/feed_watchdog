import httpx
import pydantic
from dependency_injector import containers, providers
from pydantic_settings import BaseSettings
from redis import asyncio as aioredis

from feed_watchdog.api_client.client import FeedWatchdogAPIClient
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.pubsub.subscriber import Subscriber
from feed_watchdog.repositories.post import RedisPostRepository
from feed_watchdog.synchronize import lock
from feed_watchdog.workers.settings import get_settings

# FIXME: remove monkey patching after this issue is resolved:
#   https://github.com/ets-labs/python-dependency-injector/issues/726
pydantic.BaseSettings = BaseSettings


def get_httpx_stream_client(token: str, timeout: int) -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(retries=2)
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(headers=headers, transport=transport, timeout=timeout)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)
    settings = providers.Singleton(get_settings)

    storage_redis_client = providers.Singleton(
        aioredis.from_url,
        url=config.redis.storage_url,
        decode_responses=True,
    )
    pub_sub_redis_client = providers.Singleton(
        aioredis.from_url,
        url=config.redis.pub_sub_url,
        decode_responses=True,
    )
    publisher = providers.Factory(
        Publisher,
        redis_client=pub_sub_redis_client,
    )
    subscriber = providers.Callable(
        Subscriber,
        redis_client=pub_sub_redis_client,
    )
    httpx_stream_client = providers.Callable(
        get_httpx_stream_client,
        token=config.app.api_token,
        timeout=config.app.api_timeout,
    )
    feed_watchdog_api_client = providers.Factory(
        FeedWatchdogAPIClient,
        client=httpx_stream_client,
        base_url=config.app.api_base_url,
    )
    post_repository = providers.Factory(
        RedisPostRepository,
        client=storage_redis_client,
    )


container = Container()
container.config.from_pydantic(get_settings(), required=True)


def wire_modules() -> None:
    container.wire(
        packages=[
            "feed_watchdog.workers.workers",
        ]
    )
    lock.init(container.storage_redis_client())
