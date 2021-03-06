from __future__ import annotations

import json
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from aioredis import Redis


class Event(Protocol):
    def as_dict(self) -> dict:
        ...


class Publisher:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def publish(self, channel, event: Event):
        await self.redis_client.publish(channel, json.dumps(event.as_dict()))
