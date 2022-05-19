import asyncio
import logging
from functools import partial
from typing import Callable, Coroutine

import aioredis
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from processors import settings
from processors.adapters import lock
from processors.adapters.pubsub import Subscriber
from processors.service_layer import process_stream, write_configuration
from processors.storage import Storage


async def run(topics: list[str], handler: Callable, subscriber: Subscriber):
    await subscriber.start(topics, on_message=handler)


def main() -> Coroutine:
    logging.basicConfig(level=logging.INFO)

    # write handlers config to file
    with open(settings.SHARED_CONFIG_PATH, "w") as f:
        write_configuration(f)

    if settings.SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO, event_level=logging.ERROR
        )
        sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[sentry_logging])

    redis = aioredis.from_url(settings.REDIS_URL)  # type: ignore
    lock.init(redis)  # TODO DI
    pubsub = redis.pubsub()
    subscriber = Subscriber(pubsub)

    topics = [settings.Topic.STREAMS.value]
    storage = Storage(redis)
    handler = partial(process_stream, storage=storage)
    return run(topics=topics, handler=handler, subscriber=subscriber)


if __name__ == "__main__":
    asyncio.run(main())
