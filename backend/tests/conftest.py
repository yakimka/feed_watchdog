import sqlite3
from contextlib import closing

import picodi
import pytest
from redis import asyncio as aioredis

from feed_watchdog.migrations.sqlite import create_tables
from feed_watchdog.repositories.user import (
    SqliteRefreshTokenRepository,
    SqliteUserRepository,
    create_sqlite_conn,
)
from feed_watchdog.rest_api.dependencies import (
    get_refresh_token_repository,
    get_user_repository,
)


@pytest.fixture(autouse=True)
async def _setup_picodi():
    yield
    singleton = picodi._picodi._scopes[picodi._picodi.SingletonScope]
    singleton._store.clear()
    await picodi.shutdown_resources()


@pytest.fixture()
def sqlite_conn():
    with closing(create_sqlite_conn(":memory:", check_same_thread=False)) as conn:
        create_tables(conn)
        yield conn


@pytest.fixture()
def user_repo(sqlite_conn):
    user_repo_ = SqliteUserRepository(sqlite_conn)
    with picodi.registry.override(get_user_repository, lambda: user_repo_):
        yield user_repo_


@pytest.fixture()
def refresh_token_repo(sqlite_conn):
    refresh_token_repo_ = SqliteRefreshTokenRepository(sqlite_conn)
    with picodi.registry.override(
        get_refresh_token_repository, lambda: refresh_token_repo_
    ):
        yield refresh_token_repo_


@pytest.fixture()
def redis_pubsub_server_url() -> str:
    return "redis://test_redis:6379/2"


@pytest.fixture()
async def redis_pubsub_server(redis_pubsub_server_url) -> aioredis.Redis:
    redis = aioredis.from_url(redis_pubsub_server_url, decode_responses=True)
    await redis.ping()
    yield redis
    await redis.flushdb()
