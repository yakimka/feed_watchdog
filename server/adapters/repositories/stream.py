from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import IStreamRepository
from domain.models import Stream


class MongoStreamRepository(IStreamRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self) -> list[Stream]:
        cursor = self.db.streams.find({}).sort("name")
        return [
            Stream.parse_obj(item) for item in await cursor.to_list(length=100)
        ]

    async def get_count(self) -> int:
        return await self.db.streams.count_documents({})

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

    async def delete_by_slug(self, slug: str) -> bool:
        result = await self.db.streams.delete_one({"slug": slug})
        return result.deleted_count > 0
