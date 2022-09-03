from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import AbstractSourceRepository
from domain.models import Source


class MongoSourceRepository(AbstractSourceRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def get_sources(self) -> list[Source]:
        cursor = self.db.sources.find({}).sort("name")
        return [
            Source.parse_obj(item) for item in await cursor.to_list(length=100)
        ]

    async def get_sources_count(self) -> int:
        return await self.db.sources.count_documents({})

    async def add_source(self, source: Source) -> str:
        try:
            new_source = await self.db.sources.insert_one(source.dict())
        except DuplicateKeyError as exc:
            if exc.details and "slug" in exc.details.get("keyPattern", {}):
                raise ValueExistsError(
                    value=source.slug, field="slug"
                ) from None
            raise
        return str(new_source.inserted_id)

    async def get_source_by_slug(self, slug: str) -> Source | None:
        result = await self.db.sources.find_one({"slug": slug})
        if result is not None:
            return Source.parse_obj(result)
        return None
