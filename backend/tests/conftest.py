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
    await picodi.init_dependencies()
    yield
    await picodi.shutdown_dependencies()


@pytest.fixture()
def sqlite_conn():
    with closing(create_sqlite_conn(":memory:", check_same_thread=False)) as conn:
        create_tables(conn)
        yield conn


@pytest.fixture(autouse=True)
def user_repo(sqlite_conn):
    user_repo_ = SqliteUserRepository(sqlite_conn)
    with picodi.registry.override(get_user_repository, lambda *_, **__: user_repo_):
        yield user_repo_


@pytest.fixture(autouse=True)
def refresh_token_repo(sqlite_conn):
    refresh_token_repo_ = SqliteRefreshTokenRepository(sqlite_conn)
    with picodi.registry.override(
        get_refresh_token_repository, lambda *_, **__: refresh_token_repo_
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
    await redis.close()
