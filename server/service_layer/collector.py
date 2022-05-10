from __future__ import annotations

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from dependency_injector.wiring import Provide, inject

from app_settings import Topic
from container import Container
from domain.events import ProcessStreamEvent

if TYPE_CHECKING:
    from adapters.publisher import Publisher
    from adapters.streams import StreamRepository


class Collector:
    @inject
    def __init__(self, streams: StreamRepository = Provide[Container.streams]):
        self.streams = streams

    @sync_to_async
    def streams_to_events(self) -> list[ProcessStreamEvent]:
        result = []
        for stream in self.streams.list():
            source = stream.source
            receiver = stream.receiver
            result.append(
                ProcessStreamEvent(
                    # TODO: add uid to Stream model
                    uid=str(stream.id),
                    message_template=(
                        stream.message_template or receiver.message_template
                    ),
                    source_url=source.url,
                    source_parser_type=source.parser_type,
                    source_encoding=source.encoding,
                    source_tags=list(source.tags),
                    receiver_type=receiver.type,
                    receiver_recipient=receiver.recipient,
                )
            )
        return result

    @inject
    async def send_events(
        self, publisher: Publisher = Provide[Container.publisher]
    ):
        for event in await self.streams_to_events():
            print(event)
            await publisher.publish(Topic.STREAMS.value, event)
