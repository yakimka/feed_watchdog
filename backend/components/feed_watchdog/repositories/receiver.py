import re

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from feed_watchdog.domain.interfaces import IReceiverRepository, ReceiverQuery
from feed_watchdog.domain.models import Receiver
from feed_watchdog.repositories.exceptions import ValueExistsError


class MongoReceiverRepository(IReceiverRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self, query: ReceiverQuery | None = None) -> list[Receiver]:
        if query is None:
            query = ReceiverQuery()
        cursor = (
            self.db.receivers.find(self._make_find_query(query))
            .sort(query.sort_by)
            .skip((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        return [
            Receiver.parse_obj(item)
            for item in await cursor.to_list(query.page_size)
        ]

    @staticmethod
    def _make_find_query(query: ReceiverQuery) -> dict:
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

    async def get_count(self, query: ReceiverQuery | None = None) -> int:
        if query is None:
            query = ReceiverQuery()
        return await self.db.receivers.count_documents(
            self._make_find_query(query)
        )

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

    async def delete(self, receiver: Receiver) -> bool:
        result = await self.db.receivers.delete_one({"slug": receiver.slug})
        return result.deleted_count > 0
