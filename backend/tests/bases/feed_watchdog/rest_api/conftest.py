from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from feed_watchdog.domain.models import UserInDB
from feed_watchdog.rest_api.core import app as fw_app
from feed_watchdog.utils.security import hash_password

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture()
def app() -> FastAPI:
    return fw_app


@pytest.fixture()
async def client(app) -> AsyncClient:
    async with AsyncClient(
        app=app, base_url="http://test", follow_redirects=True, timeout=2
    ) as client:
        yield client


@pytest.fixture()
async def admin_user(user_repo):
    user = UserInDB(
        id="4618a85f-3881-4e05-8b63-ee2c45d35980",
        email="me@localhost",
        password=hash_password("12345678"),
    )
    await user_repo.create_user(user)
    return user
