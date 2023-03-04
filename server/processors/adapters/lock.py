import logging
from asyncio import sleep
from functools import wraps
from typing import Any, Callable, TypeVar

from aioredis import Redis
from aioredis.exceptions import LockNotOwnedError
from aioredis.lock import Lock

from processors.adapters.error_tracking import write_warn_message

logger = logging.getLogger(__name__)

_redis: Redis


def init(redis_client: Redis):
    global _redis
    _redis = redis_client


F = TypeVar("F", bound=Callable[..., Any])


def async_lock(
    key: str | Callable[..., str], wait_time=1.0, lock_timeout=10.0
) -> Callable[[F], F]:
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            lock_key = key
            if callable(lock_key):
                lock_key = lock_key(*args, **kwargs)
            try:
                async with Lock(
                    _redis, lock_key, timeout=lock_timeout  # noqa: F821
                ):
                    res = await func(*args, **kwargs)
                    await sleep(wait_time)
                    return res
            except LockNotOwnedError:
                write_warn_message(
                    f"Lock {lock_key} is not owned", logger=logger
                )

        return wrapped

    return wrapper
