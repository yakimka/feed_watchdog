from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from picodi import Provide, inject

from feed_watchdog.domain.interfaces import IStreamRepository, StreamQuery
from feed_watchdog.fetchers.stream import MongoStreamFetcher
from feed_watchdog.repositories.stream import MongoStreamRepository
from feed_watchdog.rest_api.dependencies import get_mongo_db

if TYPE_CHECKING:
    from feed_watchdog.domain.models import StreamWithRelations


@inject
def get_stream_repo(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> IStreamRepository:
    return MongoStreamRepository(db)


@inject
async def get_by_slug(
    slug: str,
    streams: IStreamRepository = Provide(get_stream_repo),
):
    stream = await streams.get_by_slug(slug)
    if stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream


class StreamFetcher(Protocol):
    async def search(
        self, query: StreamQuery = StreamQuery()
    ) -> list[StreamWithRelations]:
        pass

    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
        pass


@inject
async def get_stream_fetcher(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> StreamFetcher:
    return MongoStreamFetcher(db)
