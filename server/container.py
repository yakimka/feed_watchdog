import aioredis
from dependency_injector import containers, providers

import app_settings
from adapters.publisher import Publisher
from adapters.streams import StreamRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_client = providers.Singleton(
        aioredis.from_url,
        url=config.REDIS_PUB_SUB_URL,
    )
    publisher = providers.Factory(
        Publisher,
        redis_client=redis_client,
    )
    streams = providers.Factory(StreamRepository)


container = Container()
container.config.from_dict(vars(app_settings))


def wire_container():
    container.wire(
        packages=[
            "adapters",
            "service_layer",
        ]
    )
