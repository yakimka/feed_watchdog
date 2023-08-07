import logging
from asyncio import sleep
from functools import wraps
from typing import Any, Callable, TypeVar

from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from redis.exceptions import LockError, LockNotOwnedError

from feed_watchdog.sentry.error_tracking import write_warn_message

logger = logging.getLogger(__name__)

_redis: Redis


def init(redis_client: Redis):
    global _redis
    _redis = redis_client


class AsyncLockError(Exception):
    pass


F = TypeVar("F", bound=Callable[..., Any])


def async_lock(
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
                    # If the lock release fails, it might be because of the
                    #   timeout and it's been stolen so we don't really care
                    pass
                except LockError as e:
                    retry_count -= 1
                    await sleep(lock_timeout)
                    logger.warning("Error: %s. Retrying...", e)

            if not retry_count:
                if raise_on_fail:
                    raise AsyncLockError(f"Can't lock {lock_key}")

                write_warn_message(f"Can't lock {lock_key}", logger=logger)

        return wrapped

    return wrapper
