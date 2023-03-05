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


def async_lock(  # noqa: C901
    key: str | Callable[..., str],
    wait_time=1.0,
    lock_timeout=10.0,
    retry: int = 3,
    raise_on_fail: bool = False,
) -> Callable[[F], F]:
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            lock_key = key
            if callable(lock_key):
                lock_key = lock_key(*args, **kwargs)

            retry_count = retry
            while retry_count:
                try:
                    async with Lock(
                        _redis, lock_key, timeout=lock_timeout  # noqa: F821
                    ):
                        res = await func(*args, **kwargs)
                        await sleep(wait_time)
                        return res
                except LockNotOwnedError:
                    retry_count -= 1
                    await sleep(lock_timeout)
                    logger.warning(
                        "Lock %s is not owned, retrying %s times",
                        lock_key,
                        retry_count,
                    )

            if not retry_count:
                if raise_on_fail:
                    raise LockNotOwnedError(f"Lock {lock_key} is not owned")

                write_warn_message(
                    f"Lock {lock_key} is not owned, skipping",
                    logger=logger,
                )

        return wrapped

    return wrapper
