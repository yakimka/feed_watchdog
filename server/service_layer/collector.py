from asgiref.sync import sync_to_async
from dependency_injector.wiring import Provide, inject

from adapters.publisher import Publisher
from adapters.streams import StreamRepository
from app_settings import Topic
from container import Container
from domain.events import ProcessStreamEvent
from domain.models import Stream


class Collector:
    @inject
    def __init__(self, streams: StreamRepository = Provide[Container.streams]):
        self.streams = streams

    @sync_to_async
    def streams_to_events(
        self, streams: list[Stream]
    ) -> list[ProcessStreamEvent]:
        result = []
        for stream in streams:
            source = stream.source
            receiver = stream.receiver
            receiver_options = (
                receiver.options | stream.receiver_options_override
            )
            result.append(
                ProcessStreamEvent(
                    uid=stream.uid,
                    squash=stream.squash,
                    message_template=(
                        stream.message_template or receiver.message_template
                    ),
                    source_fetcher_type=source.fetcher_type,
                    source_fetcher_options=source.fetcher_options,
                    source_parser_type=source.parser_type,
                    source_parser_options=source.parser_options,
                    source_tags=list(source.tags),
                    receiver_type=receiver.type,
                    receiver_options=receiver_options,
                    modifiers=stream.modifiers,
                )
            )
        return result

    @inject
    async def send_events(
        self,
        cron_interval: str = "",
        publisher: Publisher = Provide[Container.publisher],
    ):
        for event in await self.streams_to_events(
            self.streams.list(cron_interval=cron_interval)
        ):
            await publisher.publish(Topic.STREAMS.value, event)
