import asyncio
import json
import logging
from collections.abc import Coroutine
from contextlib import suppress
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Literal,
    Optional,
    Protocol,
    TypedDict,
)

import async_timeout
from dacite import from_dict
from redis import asyncio as aioredis

from processors.domain import events

logger = logging.getLogger(__name__)


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
    def __init__(
        self,
        pubsub: aioredis.client.PubSub,
        redis_client: aioredis.Redis = None,
        topic_name: str = None,
        group_id: str = None,
        consumer_id: str = None,
        messages_per_read: int | None = 1000,
    ):
        self.pubsub = pubsub
        self._redis_client = redis_client
        self._topic_name = topic_name
        self._group_id = group_id
        self._consumer_id = consumer_id
        self._messages_per_read = messages_per_read
        self._is_initialized = False

    async def start(
        self, topics, on_message: Callable[[Any], Coroutine[Any, Any, None]]
    ):
        await self.pubsub.subscribe(*topics)
        tasks = []
        while True:
            with suppress(asyncio.TimeoutError):
                async with async_timeout.timeout(1):
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        event = _parse_event(message)
                        task = asyncio.create_task(on_message(event))
                        tasks.append(task)
                    await asyncio.sleep(0.01)

            if len(tasks) >= 100:
                await asyncio.gather(*tasks)
                tasks = []

    async def __aiter__(self) -> AsyncGenerator[tuple[str, dict], None]:
        check_backlog = True
        while check_backlog:
            msg_id = None
            async for msg_id, msg_data in self.read(message_id="earliest"):
                yield msg_id, msg_data
            check_backlog = msg_id is not None

        while True:
            async for msg_id, msg_data in self.read(message_id="latest"):
                yield msg_id, msg_data

    async def read(
        self, message_id: str | Literal["latest", "earliest"] = "latest"
    ) -> AsyncGenerator[tuple[str, dict], None]:
        await self._init_group_and_stream()
        response = await self._redis_client.xreadgroup(
            groupname=self._group_id,
            consumername=self._consumer_id,
            streams={self._topic_name: self._parse_message_id(message_id)},
            count=self._messages_per_read,
        )
        for stream_name, stream_data in response:
            for msg_id, msg_data in stream_data:
                yield msg_id, msg_data

    def _parse_message_id(self, message_id: str):
        if message_id == "latest":
            message_id = ">"
        elif message_id == "earliest":
            message_id = "0"
        return message_id

    async def _init_group_and_stream(self) -> None:
        if self._is_initialized:
            return
        exists = await self._redis_client.exists(self._topic_name)
        if not exists:
            logger.info("init redis stream and consumer group")
            await self._redis_client.xgroup_create(
                name=self._topic_name, groupname=self._group_id, mkstream=True
            )
        else:
            groups = await self._redis_client.xinfo_groups(self._topic_name)
            if all(group["name"] != self._group_id for group in groups):
                logger.info("init consumer group on existing stream")
                # set id = '0' to make sure this new consumer group will catch up existing messages in stream
                await self._redis_client.xgroup_create(
                    name=self._topic_name, groupname=self._group_id, id="0"
                )
        self._is_initialized = True

    async def commit(self, msg_id: str) -> None:
        await self._redis_client.xack(self._topic_name, self._group_id, msg_id)


class Message(TypedDict):
    type: str
    pattern: Optional[bytes]
    channel: Optional[bytes]
    data: bytes


def _parse_event(message: Message) -> Event:
    data = json.loads(message["data"].decode("utf-8"))
    event_class = getattr(events, data.pop("__event_name__"))
    return from_dict(data_class=event_class, data=data)
