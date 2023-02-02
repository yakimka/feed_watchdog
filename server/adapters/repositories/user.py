import re

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import IStreamRepository, IUserRepository, StreamQuery
from domain.models import Stream, UserInDB


class MongoStreamRepository(IStreamRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def find(self, query: StreamQuery = StreamQuery()) -> list[Stream]:
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

    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
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

    async def delete_by_slug(self, slug: str) -> bool:
        result = await self.db.streams.delete_one({"slug": slug})
        return result.deleted_count > 0


class MongoUserRepository(IUserRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def get_user_by_id(self, id: str) -> UserInDB | None:
        result = await self.db.users.find_one({"id": id})
        if result is not None:
            return UserInDB.parse_obj(result)
        return None

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        result = await self.db.users.find_one({"email": email})
        if result is not None:
            return UserInDB.parse_obj(result)
        return None

    async def create_user(self, user: UserInDB) -> str:
        try:
            new_user = await self.db.users.insert_one(user.dict())
        except DuplicateKeyError as exc:
            if exc.details and "email" in exc.details.get("keyPattern", {}):
                raise ValueExistsError(
                    value=user.email, field="email"
                ) from None
            raise
        return str(new_user.inserted_id)