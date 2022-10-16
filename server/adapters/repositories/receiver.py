from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import IReceiverRepository
from domain.models import Receiver


class MongoReceiverRepository(IReceiverRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self) -> list[Receiver]:
        cursor = self.db.receivers.find({}).sort("name")
        return [
            Receiver.parse_obj(item)
            for item in await cursor.to_list(length=100)
        ]

    async def get_count(self) -> int:
        return await self.db.receivers.count_documents({})

    async def add(self, receiver: Receiver) -> str:
        try:
            new_receiver = await self.db.receivers.insert_one(receiver.dict())
        except DuplicateKeyError as exc:
            if exc.details and "slug" in exc.details.get("keyPattern", {}):
                raise ValueExistsError(
                    value=receiver.slug, field="slug"
                ) from None
            raise
        return str(new_receiver.inserted_id)

    async def update(self, slug: str, receiver: Receiver) -> bool:
        result = await self.db.receivers.replace_one(
            {"slug": slug}, receiver.dict()
        )
        return result.matched_count > 0

    async def get_by_slug(self, slug: str) -> Receiver | None:
        result = await self.db.receivers.find_one({"slug": slug})
        if result is not None:
            return Receiver.parse_obj(result)
        return None

    async def delete_by_slug(self, slug: str) -> bool:
        result = await self.db.receivers.delete_one({"slug": slug})
        return result.deleted_count > 0