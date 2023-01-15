import re

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from domain.interfaces import StreamQuery


class SourceInStreamList(BaseModel):
    name: str
    slug: str


class ReceiverInStreamList(BaseModel):
    name: str
    slug: str


class StreamInList(BaseModel):
    slug: str
    source: SourceInStreamList
    receiver: ReceiverInStreamList
    intervals: list[str]
    active: bool


class MongoStreamFetcher:
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def search(
        self, query: StreamQuery = StreamQuery()
    ) -> list[StreamInList]:
        cursor = (
            self.db.streams.find(self._make_find_query(query))
            .sort(query.sort_by)
            .skip((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )

        streams = await cursor.to_list(query.page_size)
        sources = await self._fetch_sources([s["source_slug"] for s in streams])
        receivers = await self._fetch_receivers(
            [s["receiver_slug"] for s in streams]
        )
        return [
            StreamInList(
                slug=s["slug"],
                source=sources[s["source_slug"]],
                receiver=receivers[s["receiver_slug"]],
                intervals=s["intervals"],
                active=s["active"],
            )
            for s in streams
        ]

    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
        return await self.db.streams.count_documents(
            self._make_find_query(query)
        )

    async def _fetch_sources(
        self, slugs: list[str]
    ) -> dict[str, SourceInStreamList]:
        result = {}
        async for item in self.db.sources.find({"slug": {"$in": slugs}}):
            result[item["slug"]] = SourceInStreamList.parse_obj(item)
        return result

    async def _fetch_receivers(
        self, slugs: list[str]
    ) -> dict[str, ReceiverInStreamList]:
        result = {}
        async for item in self.db.receivers.find({"slug": {"$in": slugs}}):
            result[item["slug"]] = ReceiverInStreamList.parse_obj(item)
        return result

    @staticmethod
    def _make_find_query(query: StreamQuery) -> dict:
        if not query.search:
            return {}
        return {"slug": {"$regex": re.compile(query.search, re.IGNORECASE)}}
