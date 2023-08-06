import asyncio
import logging
import uuid

from dependency_injector.wiring import Provide, inject

from feed_watchdog.api_client.client import FeedWatchdogAPIClient, StreamResp
from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.events import PostParsed
from feed_watchdog.handlers import HandlerType, get_handler_by_name
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.post import RedisPostRepository
from feed_watchdog.sentry.error_tracking import write_warn_message
from feed_watchdog.workers.container import Container, container
from feed_watchdog.workers.settings import Settings

logger = logging.getLogger(__name__)


class ProcessStreamsByScheduleWorker(BaseCommand):
    @inject
    def setup(
        self,
        settings: Settings = Provide[Container.settings],
        post_repository: RedisPostRepository = Provide[
            Container.post_repository
        ],
        publisher: Publisher = Provide[Container.publisher],
        api_client: FeedWatchdogAPIClient = Provide[
            Container.feed_watchdog_api_client
        ],
    ):
        self._settings = settings
        self._api_client = api_client
        self._subscriber = container.subscriber(
            topic_name=self._settings.app.post_parsed_topic,
            group_id=f"send_parsed_posts",
            consumer_id=uuid.uuid4().hex,
        )

    def handle(self, args):
        asyncio.run(self.process_posts(), debug=True)

    async def process_posts(self) -> None:
        async for msg_id, msg_data in self._subscriber:
            event = PostParsed.from_dict(msg_data)
            stream = await self.receive_stream(event.stream_slug)
            if not stream:
                write_warn_message(f"Can't find stream {event.stream_slug}")
                continue

            receiver = get_handler_by_name(
                name=stream.receiver.type,
                type=HandlerType.receivers.value,
                options={
                    **stream.receiver.options,
                    **stream.receiver_options_override,
                },
            )
            await receiver(
                [event.post],
                template=stream.message_template,
                squash=stream.squash,
            )
            self._subscriber.commit(msg_id)
            logger.info(
                "New post with id %s sent to %s (%s)",
                event.post.id,
                stream.receiver.type,
                event.slug,
            )

    async def receive_stream(self, stream_slug: str) -> StreamResp | None:
        # TODO: cache for 10 minutes
        return await self._api_client.get_stream(stream_slug)
