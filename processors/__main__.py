import asyncio
from functools import partial
from typing import Callable, Coroutine

import aioredis

from processors import settings
from processors.adapters import lock
from processors.adapters.pubsub import Subscriber
from processors.service_layer import process_stream
from processors.storage import Storage


async def run(topics: list[str], handler: Callable, subscriber: Subscriber):
    await subscriber.start(topics, on_message=handler)


def main() -> Coroutine:
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
