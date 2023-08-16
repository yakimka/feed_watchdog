import re

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from feed_watchdog.domain.interfaces import IStreamRepository, StreamQuery
from feed_watchdog.domain.models import Stream
from feed_watchdog.repositories.exceptions import ValueExistsError


class MongoStreamRepository(IStreamRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self, query: StreamQuery | None = None) -> list[Stream]:
        if query is None:
            query = StreamQuery()

        cursor = (
            self.db.streams.find(self._make_find_query(query))
            .sort(query.sort_by)
            .skip((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        return [
            Stream.parse_obj(item)
            for item in await cursor.to_list(query.page_size)
        ]

    @staticmethod
    def _make_find_query(query: StreamQuery) -> dict:
        if not query.search:
            return {}
        return {
            "slug": {"$regex": re.compile(f"^{query.search}$", re.IGNORECASE)}
        }

    async def get_count(self, query: StreamQuery | None = None) -> int:
        if query is None:
            query = StreamQuery()
        return await self.db.streams.count_documents(
            self._make_find_query(query)
        )

    async def add(self, stream: Stream) -> str:
        try:
            new_stream = await self.db.streams.insert_one(stream.dict())
        except DuplicateKeyError as exc:
            if exc.details and "slug" in exc.details.get("keyPattern", {}):
                raise ValueExistsError(
                    value=stream.slug, field="slug"
                ) from None
            raise
        return str(new_stream.inserted_id)

    async def update(self, slug: str, stream: Stream) -> bool:
        result = await self.db.streams.replace_one(
            {"slug": slug}, stream.dict()
        )
        return result.matched_count > 0

    async def get_by_slug(self, slug: str) -> Stream | None:
        result = await self.db.streams.find_one({"slug": slug})
        if result is not None:
            return Stream.parse_obj(result)
        return None

    async def get_by_source_slug(self, source_slug: str) -> list[Stream]:
        cursor = self.db.streams.find({"source_slug": source_slug})
        return [
            Stream.parse_obj(item) for item in await cursor.to_list(length=None)
        ]

    async def get_by_receiver_slug(self, receiver_slug: str) -> list[Stream]:
        cursor = self.db.streams.find({"receiver_slug": receiver_slug})
        return [
            Stream.parse_obj(item) for item in await cursor.to_list(length=None)
        ]

    async def delete_by_slug(self, slug: str) -> bool:
        result = await self.db.streams.delete_one({"slug": slug})
        return result.deleted_count > 0
