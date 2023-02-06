import asyncio
import getpass
from uuid import uuid4

from pydantic import BaseModel

from api.deps.user import get_user_repo
from commands.core import BaseCommand
from container import container
from domain.models import UserInDB
from utils.security import hash_password


class User(BaseModel):
    email: str
    password: str


class CreateUserCommand(BaseCommand):
    async def run(self, data: User):
        user_repo = await get_user_repo(
            db=container.mongo_client().get_database()
        )
        user = await user_repo.get_user_by_email(data.email)
        if user is not None:
            raise RuntimeError("User already exists")

        new_user = UserInDB(
            id=str(uuid4()),
            email=data.email,
            password=hash_password(data.password),
        )
        await user_repo.create_user(new_user)
        return new_user


if __name__ == "__main__":
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    asyncio.run(CreateUserCommand().run(User(email=email, password=password)))
