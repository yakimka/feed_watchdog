import aioredis
from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.publisher import Publisher
from app_settings import get_settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)
    settings = providers.Singleton(get_settings)

    redis_client = providers.Singleton(
        aioredis.from_url,
        url=config.redis.pub_sub_url,
    )
    mongo_client = providers.Singleton(  # type: ignore
        AsyncIOMotorClient,
        config.mongo.url,
    )
    publisher = providers.Factory(
        Publisher,
        redis_client=redis_client,
    )


container = Container()
container.config.from_pydantic(get_settings(), required=True)


def wire_modules() -> None:
    container.wire(
        packages=[
            "auth",
            "api.deps",
            "api.routers",
        ]
    )
