import asyncio
import getpass
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel

from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.interfaces import IUserRepository
from feed_watchdog.domain.models import UserInDB
from feed_watchdog.rest_api.container import Container
from feed_watchdog.utils.security import hash_password


class User(BaseModel):
    email: str
    password: str


class CreateUserCommand(BaseCommand):
    def handle(self, args):
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        asyncio.run(self._handle(User(email=email, password=password)))

    @inject
    async def _handle(
        self,
        user_data: User,
        user_repo: IUserRepository = Provide[Container.user_repository],
    ):
        user = await user_repo.get_user_by_email(user_data.email)
        if user is not None:
            raise RuntimeError("User already exists")

        new_user = UserInDB(
            id=str(uuid4()),
            email=user_data.email,
            password=hash_password(user_data.password),
        )
        await user_repo.create_user(new_user)
        return new_user
