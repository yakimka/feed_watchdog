from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Protocol

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from picodi import SingletonScope, dependency, inject
from picodi.integrations.fastapi import Provide
from redis import asyncio as aioredis

from feed_watchdog.domain.interfaces import (
    IReceiverRepository,
    IRefreshTokenRepository,
    ISourceRepository,
    IStreamRepository,
    StreamQuery,
)
from feed_watchdog.fetchers.stream import MongoStreamFetcher
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.processor import FileProcessorsConfigRepo
from feed_watchdog.repositories.receiver import MongoReceiverRepository
from feed_watchdog.repositories.source import MongoSourceRepository
from feed_watchdog.repositories.stream import MongoStreamRepository
from feed_watchdog.repositories.user import (
    MongoRefreshTokenRepository,
    MongoUserRepository,
)
from feed_watchdog.rest_api.settings import Settings, get_settings
from feed_watchdog.synchronize import lock

if TYPE_CHECKING:
    from feed_watchdog.domain.models import StreamWithRelations


@dependency(scope_class=SingletonScope)
@inject
async def get_redis(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(url=settings.redis.pub_sub_url)
    async with redis as conn:
        yield conn


@inject
async def init_lock(
    redis: aioredis.Redis = Provide(get_redis),
) -> None:
    return lock.init(redis)


@inject
def get_publisher(redis: aioredis.Redis = Provide(get_redis)) -> Publisher:
    return Publisher(redis)


@dependency(scope_class=SingletonScope)
@inject
async def get_mongo_db(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo.url)
    try:
        yield client.get_database()
    finally:
        client.close()


@inject
async def get_receiver_repository(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> IReceiverRepository:
    return MongoReceiverRepository(db)


@inject
async def get_source_repository(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> ISourceRepository:
    return MongoSourceRepository(db)


@inject
async def get_stream_repository(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> IStreamRepository:
    return MongoStreamRepository(db)


class StreamFetcher(Protocol):
    async def search(
        self, query: StreamQuery = StreamQuery()
    ) -> list[StreamWithRelations]:
        pass

    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
        pass


@inject
async def get_stream_fetcher(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> StreamFetcher:
    return MongoStreamFetcher(db)


@inject
async def get_refresh_token_repository(
    db: AsyncIOMotorDatabase = Provide(get_mongo_db),
) -> IRefreshTokenRepository:
    return MongoRefreshTokenRepository(db)


@inject
async def get_user_repository(
    mongo_db: AsyncIOMotorDatabase = Provide(get_mongo_db),
) -> MongoUserRepository:
    return MongoUserRepository(db=mongo_db)


@inject
def get_processors_conf_repository(
    settings: Settings = Provide(get_settings),
) -> FileProcessorsConfigRepo:
    return FileProcessorsConfigRepo(handlers_conf_path=settings.app.handlers_conf_path)


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
