from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING, Awaitable, Callable, Iterable

from aiogram import Bot

from processors.adapters.lock import async_lock
from processors.domain.logic import make_message_from_template
from processors.handlers import HandlerOptions, HandlerType, register_handler

if TYPE_CHECKING:
    from processors.domain.models import Post

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TelegramBotOptions(HandlerOptions):
    DESCRIPTIONS = {
        "chat_id": ("Chat ID", "Telegram chat id"),
        "disable_link_preview": ("Disable link preview", ""),
    }

    chat_id: str
    disable_link_preview: bool = False


@register_handler(
    type=HandlerType.receivers.value,
    name="telegram_bot",
    options=TelegramBotOptions,
)
class TelegramBot:
    MAX_MESSAGE_LENGTH = 500
    MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20
    pause_between_send = 60 / MAX_MESSAGES_PER_MINUTE_PER_GROUP  # seconds

    def __init__(self, name: str, token: str):
        self._name = name
        self._token = token
        self.bot = Bot(token=self._token)

    def _lock_key(self, *_, **__):
        return self._name

    async def __call__(
        self,
        posts: Iterable[Post],
        *,
        template: str,
        squash: bool = False,
        options: TelegramBotOptions,
        callback: Callable[[Post], Awaitable] = None,
    ) -> None:
        if squash:
            await self._send_squashed_message(
                posts,
                template=template,
                options=options,
                callback=callback,
            )
        else:
            await self._send_separate_messages(
                posts,
                template=template,
                options=options,
                callback=callback,
            )

    async def _send_separate_messages(
        self,
        posts: Iterable[Post],
        *,
        template: str,
        options: TelegramBotOptions,
        callback: Callable[[Post], Awaitable] = None,
    ) -> None:
        for post in posts:
            message = make_message_from_template(
                template, **post.template_kwargs()
            )
            await self._send_message(
                message=message,
                chat_id=options.chat_id,
                disable_link_preview=options.disable_link_preview,
            )
            if callback is not None:
                await callback(post)

    async def _send_squashed_message(
        self,
        posts: Iterable[Post],
        *,
        template: str,
        options: TelegramBotOptions,
        callback: Callable[[Post], Awaitable] = None,
    ) -> None:
        posts = list(posts)
        parts = []
        delimiter = "\n-----\n"
        for post in posts:
            message = make_message_from_template(
                template, **post.template_kwargs()
            )
            parts.extend((message.strip(), delimiter))
        if parts:
            parts.pop()

        added_truncated_message = False
        while sum(len(part) for part in parts) > self.MAX_MESSAGE_LENGTH:
            if not added_truncated_message:
                parts.append("\nTruncated...")
                added_truncated_message = True
            parts.pop(-2)

        message = "".join(parts)
        await self._send_message(
            message=message,
            chat_id=options.chat_id,
            disable_link_preview=options.disable_link_preview,
        )
        if callback is not None:
            for post in posts:
                await callback(post)

    @async_lock(key=_lock_key, wait_time=pause_between_send)
    async def _send_message(
        self, message: str, chat_id: str, disable_link_preview: bool
    ) -> None:
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=disable_link_preview,
        )
        logger.info("Sent post to %s (%s)", self._name, chat_id)
