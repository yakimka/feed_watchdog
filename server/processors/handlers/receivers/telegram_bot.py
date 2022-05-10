from __future__ import annotations

import string
from typing import TYPE_CHECKING

from aiogram import Bot

from processors.adapters.lock import async_lock

if TYPE_CHECKING:
    from processors.domain.models import Post


class TelegramBot:
    MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20
    pause_between_send = 60 / MAX_MESSAGES_PER_MINUTE_PER_GROUP  # seconds

    def __init__(self, name: str, token: str):
        self._name = name
        self._token = token
        self.bot = Bot(token=self._token)

    def _lock_key(self, *_, **__):
        return self._name

    @async_lock(key=_lock_key, wait_time=pause_between_send)
    async def send(
        self,
        post: Post,
        *,
        chat_id: str,
        disable_link_preview: bool = False,
    ) -> None:
        await self.bot.send_message(
            chat_id=chat_id,
            text=self._make_message_text(post),
            parse_mode="HTML",
            disable_web_page_preview=disable_link_preview,
        )

    @staticmethod
    def _make_message_text(post: Post):
        template = string.Template(post.message_template)
        data = post.template_kwargs()
        return template.safe_substitute(data)


class Sender(TelegramBot):
    pass
