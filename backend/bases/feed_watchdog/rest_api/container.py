import pydantic
from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from redis import asyncio as aioredis

from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.processor import FileProcessorsConfigRepo
from feed_watchdog.repositories.user import MongoUserRepository
from feed_watchdog.rest_api.settings import get_settings

# FIXME: remove monkey patching after this issue is resolved:
#   https://github.com/ets-labs/python-dependency-injector/issues/726
pydantic.BaseSettings = BaseSettings


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
    mongo_db = providers.Callable(
        lambda mongo_client: mongo_client.get_database(),
        mongo_client=mongo_client,
    )
    publisher = providers.Factory(
        Publisher,
        redis_client=redis_client,
    )
    user_repository = providers.Factory(
        MongoUserRepository,
        db=mongo_db,
    )
    processors_conf_repository = providers.Factory(
        FileProcessorsConfigRepo,
        handlers_conf_path=config.app.handlers_conf_path,
    )


container = Container()
container.config.from_pydantic(get_settings(), required=True)


def wire_modules() -> None:
    container.wire(
        packages=[
            "feed_watchdog.rest_api.auth",
            "feed_watchdog.rest_api.commands",
            "feed_watchdog.rest_api.deps",
            "feed_watchdog.rest_api.routers",
        ]
    )
