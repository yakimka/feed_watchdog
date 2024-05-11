import logging
import uuid

from picodi import Provide, inject

from feed_watchdog.api_client.client import FeedWatchdogAPIClient, StreamResp
from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.events import MessageBatch
from feed_watchdog.handlers import HandlerType, get_handler_by_name
from feed_watchdog.pubsub.subscriber import Subscriber
from feed_watchdog.workers.dependencies import get_feed_watchdog_api_client
from feed_watchdog.workers.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class ProcessStreamsByScheduleWorker(BaseCommand):
    @inject
    def __init__(
        self,
        settings: Settings = Provide(get_settings),
        api_client: FeedWatchdogAPIClient = Provide(get_feed_watchdog_api_client),
    ) -> None:
        self._settings = settings
        self._api_client = api_client
        self._subscriber = Subscriber(
            topic_name=self._settings.app.messages_topic,
            group_id="send_messages",
            consumer_id=uuid.uuid4().hex,
        )

    async def handle(self, args) -> None:  # noqa: U100
        await self.process_messages()

    async def process_messages(self) -> None:
        logger.info("Start processing messages for sending")
        async for msg_id, msg_data in self._subscriber:
            message_batch = MessageBatch.from_dict(msg_data)
            stream = await self.receive_stream(message_batch.stream_slug)
            if not stream:
                logger.warning("Can't find stream %s", message_batch.stream_slug)
                await self._subscriber.commit(msg_id)
                continue

            receiver = get_handler_by_name(
                name=stream.receiver.type,
                type=HandlerType.receivers.value,
                options={
                    **stream.receiver.options,
                    **stream.receiver_options_override,
                },
            )
            await receiver(message_batch.messages)
            await self._subscriber.commit(msg_id)
            logger.info(
                "Message batch sent to %s (%s)",
                stream.receiver.type,
                message_batch.stream_slug,
            )

    async def receive_stream(self, stream_slug: str) -> StreamResp | None:
        # TODO: cache for 10 minutes
        return await self._api_client.get_stream(stream_slug)
