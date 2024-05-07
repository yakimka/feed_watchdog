from typing import Any, AsyncGenerator, Callable

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from picodi import Provide, inject, resource
from redis import asyncio as aioredis

from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.processor import FileProcessorsConfigRepo
from feed_watchdog.repositories.user import MongoUserRepository
from feed_watchdog.rest_api.settings import Settings, get_settings


@inject
@resource
async def get_redis(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(url=settings.redis.pub_sub_url)
    try:
        yield redis
    finally:
        await redis.aclose()  # type: ignore[attr-defined]


@inject
def get_publisher(redis: aioredis.Redis = Provide(get_redis)) -> Publisher:
    return Publisher(redis)


@inject
@resource
async def get_mongo_db(
    settings: Settings = Provide(get_settings),
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client = AsyncIOMotorClient(settings.mongo.url)
    try:
        yield client.get_database()
    finally:
        client.close()


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
