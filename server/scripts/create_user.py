import asyncio
import getpass
from uuid import uuid4

from pydantic import BaseModel

from api.deps.mongo import get_client, get_db
from api.deps.user import get_user_repo
from domain.models import UserInDB
from utils.security import hash_password


class User(BaseModel):
    email: str
    password: str


async def create_user(data: User):
    user_repo = await get_user_repo(db=get_db(client=get_client()))
    user = await user_repo.get_user_by_email(data.email)
    if user is not None:
        raise RuntimeError("User already exists")

    new_user = UserInDB(
        id=str(uuid4()), email=data.email, password=hash_password(data.password)
    )
    await user_repo.create_user(new_user)
    return new_user


if __name__ == "__main__":
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    asyncio.run(create_user(User(email=email, password=password)))
