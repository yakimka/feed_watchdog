from functools import lru_cache

from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.mongo import get_client as get_mongo_client


@lru_cache(maxsize=1)
def get_client() -> AsyncIOMotorClient:
    return get_mongo_client()


@lru_cache(maxsize=1)
def get_db(client: AsyncIOMotorClient = Depends(get_client)):
    return client.feed_watchdog
