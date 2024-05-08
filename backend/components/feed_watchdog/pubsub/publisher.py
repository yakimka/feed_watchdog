import json
import logging
from typing import Any

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis_client = redis_client

    async def publish(self, channel, data: dict[str, Any]) -> None:
        encoded_data = {
            key: json.dumps(value).encode("utf-8") for key, value in data.items()
        }
        await self._redis_client.xadd(channel, encoded_data)
