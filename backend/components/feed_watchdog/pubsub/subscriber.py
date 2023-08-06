import json
import logging
from typing import Any, AsyncGenerator, Literal

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class Subscriber:
    def __init__(
        self,
        *,
        redis_client: aioredis.Redis,
        topic_name: str,
        group_id: str,
        consumer_id: str,
        messages_per_read: int | None = 1000,
        autoclaim_min_idle_time: int = 60 * 1000,  # ms
        check_backlog_every: int = 100,
    ):
        self._redis_client = redis_client
        self._topic_name = topic_name
        self._group_id = group_id
        self._consumer_id = consumer_id
        self._messages_per_read = messages_per_read
        self._autoclaim_min_idle_time = autoclaim_min_idle_time
        self._check_backlog_every = check_backlog_every
        self._is_initialized = False

    async def __aiter__(self) -> AsyncGenerator[tuple[str, dict], None]:
        iterations = self._check_backlog_every
        while True:
            async for msg_id, msg_data in self.read(message_id="latest"):
                yield msg_id, msg_data
            iterations = max(0, iterations - 1)

            if self._check_backlog_every and iterations == 0:
                async for msg_id, msg_data in self.autoclaim():
                    yield msg_id, msg_data
                iterations = self._check_backlog_every

    async def read(
        self, message_id: str | Literal["latest", "earliest"] = "latest"
    ) -> AsyncGenerator[tuple[str, dict], None]:
        await self._init_group_and_stream()
        response = await self._redis_client.xreadgroup(
            groupname=self._group_id,
            consumername=self._consumer_id,
            streams={self._topic_name: self._parse_message_id(message_id)},
            count=self._messages_per_read,
            block=100,
        )
        for _stream_name, stream_data in response:
            for msg_id, msg_data in stream_data:
                yield msg_id, self._decode_message_data(msg_data)

    async def autoclaim(self) -> AsyncGenerator[tuple[str, dict], None]:
        response = await self._redis_client.xautoclaim(
            name=self._topic_name,
            groupname=self._group_id,
            consumername=self._consumer_id,
            min_idle_time=self._autoclaim_min_idle_time,
            count=self._messages_per_read,
        )
        for stream_data in response[1]:
            msg_id, msg_data = stream_data
            yield msg_id, self._decode_message_data(msg_data)

    def _parse_message_id(self, message_id: str):
        if message_id == "latest":
            message_id = ">"
        elif message_id == "earliest":
            message_id = "0"
        return message_id

    def _decode_message_data(
        self, message_data: dict[str, bytes]
    ) -> dict[str, Any]:
        decoded_data = {}
        for key, value in message_data.items():
            decoded_data[key] = json.loads(value)
        return decoded_data

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
                # set id = '0' to make sure this new consumer group
                #   will catch up existing messages in stream
                await self._redis_client.xgroup_create(
                    name=self._topic_name, groupname=self._group_id, id="0"
                )
        self._is_initialized = True

    async def commit(self, msg_id: str) -> None:
        await self._redis_client.xack(self._topic_name, self._group_id, msg_id)
