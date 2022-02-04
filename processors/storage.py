from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aioredis import Redis


class Storage:
    def __init__(self, client: Redis):
        self._client = client

    async def sent_posts_count(
        self, stream_uid: str, receiver_type: str
    ) -> int:
        return await self._client.scard(
            self._make_sent_posts_key(stream_uid, receiver_type)
        )

    async def post_was_sent(
        self, post_id: str, stream_uid: str, receiver_type: str
    ) -> bool:
        return await self._client.sismember(
            self._make_sent_posts_key(stream_uid, receiver_type), post_id
        )

    async def save_post_sent_flag(
        self, post_id: str, stream_uid: str, receiver_type: str
    ) -> None:
        await self._client.sadd(
            self._make_sent_posts_key(stream_uid, receiver_type), post_id
        )

    @staticmethod
    def _make_sent_posts_key(stream_uid: str, receiver_type: str) -> str:
        return f"sent_posts:{stream_uid}_{receiver_type}"
