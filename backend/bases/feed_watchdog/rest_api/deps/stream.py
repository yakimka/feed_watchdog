from __future__ import annotations

from fastapi import HTTPException
from picodi import inject
from picodi.integrations.fastapi import Provide

from feed_watchdog.domain.interfaces import IStreamRepository
from feed_watchdog.rest_api.dependencies import get_stream_repository


@inject
async def get_by_slug(
    slug: str,
    streams: IStreamRepository = Provide(get_stream_repository, wrap=True),
):
    stream = await streams.get_by_slug(slug)
    if stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream
