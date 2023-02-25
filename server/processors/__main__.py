import asyncio
import logging
from typing import Callable, Coroutine

import aioredis

from adapters import sentry
from processors import settings
from processors.adapters import lock
from processors.adapters.pubsub import Subscriber
from processors.service_layer import process_stream, write_configuration
from processors.storage import Storage

logger = logging.getLogger(__name__)


async def run(topics: list[str], handler: Callable, subscriber: Subscriber):
    await subscriber.start(topics, on_message=handler)


def main() -> Coroutine:
    logging.basicConfig(level=logging.INFO)

    # write handlers config to file
    with open(settings.SHARED_CONFIG_PATH, "w") as f:
        write_configuration(f)

    sentry.setup_logging(settings.SENTRY_DSN)

    redis = aioredis.from_url(settings.REDIS_URL)  # type: ignore
    lock.init(redis)  # TODO DI
    pubsub = redis.pubsub()
    subscriber = Subscriber(pubsub)

    topics = [settings.Topic.STREAMS.value]
    storage = Storage(redis)

    async def handler(event):
        try:
            return await process_stream(event, storage=storage)
        except Exception as e:  # noqa: PLW0703
            logger.exception(e)

    logger.info("Starting processing")
    return run(topics=topics, handler=handler, subscriber=subscriber)


if __name__ == "__main__":
    asyncio.run(main())
