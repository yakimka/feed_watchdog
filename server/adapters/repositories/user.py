from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from api.exceptions import ValueExistsError
from domain.interfaces import IUserRepository
from domain.models import UserInDB


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
