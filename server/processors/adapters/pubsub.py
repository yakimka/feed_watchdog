from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import TYPE_CHECKING, Protocol, TypedDict

import async_timeout

from processors.domain import events

if TYPE_CHECKING:
    from collections.abc import Coroutine
    from typing import Any, Callable, Optional

    import aioredis


class Event(Protocol):
    def __init__(self, *args, **kwargs):
        pass

    def as_dict(self) -> dict:
        pass


class Publisher:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def publish(self, channel, event: Event):
        await self.redis_client.publish(channel, json.dumps(event.as_dict()))


class Subscriber:
    def __init__(self, pubsub: aioredis.client.PubSub):
        self.pubsub = pubsub

    async def start(
        self, topics, on_message: Callable[[Any], Coroutine[Any, Any, None]]
    ):
        await self.pubsub.subscribe(*topics)
        while True:
            with suppress(asyncio.TimeoutError):
                async with async_timeout.timeout(1):
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        event = _parse_event(message)
                        print(event)
                        asyncio.create_task(on_message(event))
                    await asyncio.sleep(0.01)


class Message(TypedDict):
    type: str
    pattern: Optional[bytes]
    channel: Optional[bytes]
    data: bytes


def _parse_event(message: Message) -> Event:
    data = json.loads(message["data"].decode("utf-8"))
    event_class = getattr(events, data.pop("__event_name__"))
    return event_class(**data)
