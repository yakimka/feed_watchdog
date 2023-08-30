import pytest
from redis import asyncio as aioredis


@pytest.fixture()
def redis_pubsub_server_url() -> str:
    return "redis://test_redis:6379/2"


@pytest.fixture()
async def redis_pubsub_server(redis_pubsub_server_url) -> aioredis.Redis:
    redis = aioredis.from_url(redis_pubsub_server_url, decode_responses=True)
    await redis.ping()
    yield redis
    await redis.flushdb()
