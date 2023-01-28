import re

from motor.motor_asyncio import AsyncIOMotorClient

from domain.interfaces import StreamQuery
from domain.models import Receiver, Source, StreamWithRelations


class MongoStreamFetcher:
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def search(
        self, query: StreamQuery = StreamQuery()
    ) -> list[StreamWithRelations]:
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
            StreamWithRelations.parse_obj(
                {
                    **s,
                    "source": sources[s["source_slug"]],
                    "receiver": receivers[s["receiver_slug"]],
                }
            )
            for s in streams
        ]

    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
        return await self.db.streams.count_documents(
            self._make_find_query(query)
        )

    async def _fetch_sources(self, slugs: list[str]) -> dict[str, Source]:
        result = {}
        async for item in self.db.sources.find({"slug": {"$in": slugs}}):
            result[item["slug"]] = Source.parse_obj(item)
        return result

    async def _fetch_receivers(self, slugs: list[str]) -> dict[str, Receiver]:
        result = {}
        async for item in self.db.receivers.find({"slug": {"$in": slugs}}):
            result[item["slug"]] = Receiver.parse_obj(item)
        return result

    @staticmethod
    def _make_find_query(query: StreamQuery) -> dict:
        filters = {}
        if query.search:
            filters["slug"] = {
                "$regex": re.compile(query.search, re.IGNORECASE)
            }
        if query.interval:
            filters["intervals"] = query.interval
        return filters
