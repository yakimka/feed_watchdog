import asyncio
import logging
import uuid
from dataclasses import asdict
from typing import Sequence

from dependency_injector.wiring import Provide, inject

from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.events import (
    Message,
    MessageBatch,
    ModifierData,
    ProcessStreamEvent,
)
from feed_watchdog.domain.models import Post
from feed_watchdog.handlers import HandlerType, get_handler_by_name
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.post import RedisPostRepository
from feed_watchdog.sentry.error_tracking import write_warn_message
from feed_watchdog.text import template_to_text
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
    ) -> None:
        self._settings = settings
        self._post_repository = post_repository
        self._publisher = publisher
        self._subscriber = container.subscriber(
            topic_name=self._settings.app.streams_topic,
            group_id="fetch_posts_from_streams",
            consumer_id=uuid.uuid4().hex,
        )

    def handle(self, args) -> None:  # noqa: U100
        asyncio.run(self.process_streams(), debug=True)

    async def process_streams(self) -> None:
        logger.info("Start processing streams for fetching")
        async for msg_id, msg_data in self._subscriber:
            event = ProcessStreamEvent.from_dict(msg_data)
            await self.process_event(event)
            await self._subscriber.commit(msg_id)

    async def process_event(self, event: ProcessStreamEvent) -> None:
        text = await self.fetch_text(event)
        if not text:
            logger.warning(
                "Can't fetch text for %s",
                event.slug,
                extra={
                    "stream_slug": event.slug,
                    "fetcher_type": event.source.fetcher_type,
                    "fetcher_options": event.source.fetcher_options,
                },
            )
            return

        posts = await self.parse_posts(event, text)
        if not posts:
            logger.warning(
                "Can't parse posts for %s",
                event.slug,
                extra={
                    "stream_slug": event.slug,
                    "text": text,
                    "parser_type": event.source.parser_type,
                    "parser_options": event.source.parser_options,
                },
            )
            return

        final_posts = await self.apply_modifiers_to_posts(
            event.modifiers, posts
        )
        events_for_sending = await self.parse_new_events(event, final_posts)
        post_ids = [
            msg.post_id
            for event in events_for_sending
            for msg in event.messages
        ]
        logger.info(
            "Sending %s events for %s", len(events_for_sending), event.slug
        )
        await self.send_events(events_for_sending)

        if left_posts := {post.post_id for post in posts} - set(post_ids):
            await self._post_repository.mark_post_as_seen(
                event.slug, *left_posts
            )

    async def fetch_text(self, event: ProcessStreamEvent) -> str | None:
        fetcher = get_handler_by_name(
            type=HandlerType.fetchers.value,
            name=event.source.fetcher_type,
            options=event.source.fetcher_options,
        )
        return await fetcher()

    async def parse_posts(
        self, event: ProcessStreamEvent, text: str
    ) -> list[Post]:
        parser = get_handler_by_name(
            name=event.source.parser_type,
            type=HandlerType.parsers.value,
            options=event.source.parser_options,
        )
        posts = await parser(text)
        mutate_posts_with_stream_data(event, posts)
        return posts

    async def apply_modifiers_to_posts(
        self, modifiers: list[ModifierData], posts: list[Post]
    ) -> list[Post]:
        for modifier in modifiers:
            modifier_func = get_handler_by_name(
                name=modifier.type,
                type=HandlerType.modifiers.value,
                options=modifier.options,
            )
            posts = await modifier_func(posts)
        return posts

    async def parse_new_events(
        self, event: ProcessStreamEvent, posts: list[Post]
    ) -> list[MessageBatch]:
        has_posts = bool(
            await self._post_repository.seen_posts_count(stream_id=event.slug)
        )
        messages = []
        for post in reversed(posts):
            if not has_posts:  # first run, don't send all posts in stream
                write_warn_message(f"First run for {event.slug}", logger=logger)
                break
            if await self._post_repository.is_post_seen(
                post.post_id, stream_id=event.slug
            ):
                continue

            post_text = template_to_text(
                event.message_template, **post.template_kwargs()
            )
            messages.append(Message(post_id=post.post_id, text=post_text))

        if not messages:
            return []

        if event.squash:
            return [MessageBatch(stream_slug=event.slug, messages=messages)]
        return [
            MessageBatch(stream_slug=event.slug, messages=[message])
            for message in messages
        ]

    async def send_events(self, events_for_sending: list[MessageBatch]) -> None:
        for event in events_for_sending:
            await self._publisher.publish(
                self._settings.app.messages_topic, data=asdict(event)
            )
            await self._post_repository.mark_post_as_seen(
                event.stream_slug, *[msg.post_id for msg in event.messages]
            )


def mutate_posts_with_stream_data(
    stream: ProcessStreamEvent,
    posts: Sequence[Post],
) -> None:
    for post in posts:
        post.post_id = _clean_post_id(post.post_id)
        post.source_tags = stream.source.tags


def _clean_post_id(post_id: str) -> str:
    return post_id.removeprefix("https://").removeprefix("http://")
