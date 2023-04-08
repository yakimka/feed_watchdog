import re

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import ISourceRepository, SourceQuery
from domain.models import Source


class MongoSourceRepository(ISourceRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self, query: SourceQuery | None = None) -> list[Source]:
        if query is None:
            query = SourceQuery()
        cursor = (
            self.db.sources.find(self._make_find_query(query))
            .sort(query.sort_by)
            .skip((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        return [
            Source.parse_obj(item)
            for item in await cursor.to_list(query.page_size)
        ]

    @staticmethod
    def _make_find_query(query: SourceQuery) -> dict:
        if not query.search:
            return {}
        return {
            "$or": [
                {"name": {"$regex": re.compile(query.search, re.IGNORECASE)}},
                {
                    "slug": {
                        "$regex": re.compile(f"^{query.search}$", re.IGNORECASE)
                    }
                },
            ]
        }

    async def get_count(self, query: SourceQuery | None = None) -> int:
        if query is None:
            query = SourceQuery()
        return await self.db.sources.count_documents(
            self._make_find_query(query)
        )

    async def get_all_tags(self) -> list[str]:
        cursor = self.db.sources.aggregate(
            [
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags"}},
                {"$project": {"_id": 0, "tag": "$_id"}},
            ]
        )
        return sorted([item["tag"] async for item in cursor])

    async def add(self, source: Source) -> str:
        try:
            new_source = await self.db.sources.insert_one(source.dict())
        except DuplicateKeyError as exc:
            if exc.details and "slug" in exc.details.get("keyPattern", {}):
                raise ValueExistsError(
                    value=source.slug, field="slug"
                ) from None
            raise
        return str(new_source.inserted_id)

    async def update(self, slug: str, source: Source) -> bool:
        result = await self.db.sources.replace_one(
            {"slug": slug}, source.dict()
        )
        return result.matched_count > 0

    async def get_by_slug(self, slug: str) -> Source | None:
        result = await self.db.sources.find_one({"slug": slug})
        if result is not None:
            return Source.parse_obj(result)
        return None

    async def delete(self, source: Source) -> bool:
        result = await self.db.sources.delete_one({"slug": source.slug})
        return result.deleted_count > 0
