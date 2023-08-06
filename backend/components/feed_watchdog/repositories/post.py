from redis.asyncio import Redis

from feed_watchdog.domain.interfaces import IPostRepository


class RedisPostRepository(IPostRepository):
    def __init__(self, client: Redis):
        self._client = client

    async def mark_post_as_seen(self, stream_id: str, *post_id: str) -> None:
        await self._client.sadd(self._make_marked_post_key(stream_id), *post_id)

    async def seen_posts_count(self, stream_id: str) -> int:
        return await self._client.scard(self._make_marked_post_key(stream_id))

    async def is_post_seen(self, post_id: str, stream_id: str) -> bool:
        return await self._client.sismember(
            self._make_marked_post_key(stream_id), post_id
        )

    @staticmethod
    def _make_marked_post_key(stream_id: str) -> str:
        return f"posts:marked:seen:{stream_id}"

    async def sent_posts_count(self, stream_id: str, receiver_type: str) -> int:
        return await self._client.scard(
            self._make_sent_posts_key(stream_id, receiver_type)
        )

    async def post_was_sent(
        self, post_id: str, stream_id: str, receiver_type: str
    ) -> bool:
        return await self._client.sismember(
            self._make_sent_posts_key(stream_id, receiver_type), post_id
        )

    async def save_post_sent_flag(
        self, post_id: str, stream_id: str, receiver_type: str
    ) -> None:
        await self._client.sadd(
            self._make_sent_posts_key(stream_id, receiver_type), post_id
        )

    @staticmethod
    def _make_sent_posts_key(stream_id: str, receiver_type: str) -> str:
        return f"sent_posts:{stream_id}_{receiver_type}"
