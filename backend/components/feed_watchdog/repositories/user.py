from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from feed_watchdog.domain.interfaces import (
    IRefreshTokenRepository,
    IUserRepository,
)
from feed_watchdog.domain.models import RefreshToken, UserInDB
from feed_watchdog.repositories.exceptions import ValueExistsError


class MongoUserRepository(IUserRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def get_user_by_id(self, id: str) -> UserInDB | None:  # noqa: PLW0622
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


class MongoRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, db: AsyncIOMotorClient) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: str) -> list[RefreshToken]:
        result = self.db.refresh_tokens.find({"user_id": user_id})
        return [RefreshToken.parse_obj(item) async for item in result]

    async def create(self, refresh_token: RefreshToken) -> str:
        new_token = await self.db.refresh_tokens.insert_one(
            refresh_token.dict()
        )
        return str(new_token.inserted_id)

    async def delete(self, token: str) -> bool:
        result = await self.db.refresh_tokens.delete_one({"token": token})
        return result.deleted_count > 0

    async def delete_all(self, user_id: str) -> bool:
        result = await self.db.refresh_tokens.delete_many({"user_id": user_id})
        return result.deleted_count > 0
