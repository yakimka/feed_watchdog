import aioredis
from aioredis import Redis
from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.publisher import Publisher
from app_settings import Settings, get_settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)
    settings: Settings = providers.Singleton(get_settings)

    redis_client: Redis = providers.Singleton(
        aioredis.from_url,
        url=config.redis.pub_sub_url,
    )
    mongo_client: AsyncIOMotorClient = providers.Singleton(
        AsyncIOMotorClient,
        config.mongo.url,
    )
    publisher: Publisher = providers.Factory(
        Publisher,
        redis_client=redis_client,
    )


container = Container()
container.config.from_pydantic(get_settings(), required=True)


def wire_modules():
    container.wire(
        packages=[
            "auth",
            "api.deps",
            "api.routers",
        ]
    )
