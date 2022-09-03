from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import ISourceRepository
from domain.models import Source


class MongoSourceRepository(ISourceRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self) -> list[Source]:
        cursor = self.db.sources.find({}).sort("name")
        return [
            Source.parse_obj(item) for item in await cursor.to_list(length=100)
        ]

    async def get_count(self) -> int:
        return await self.db.sources.count_documents({})

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

    async def delete_by_slug(self, slug: str) -> bool:
        result = await self.db.sources.delete_one({"slug": slug})
        return result.deleted_count > 0
