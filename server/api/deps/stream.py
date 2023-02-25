from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.fetchers import MongoStreamFetcher
from adapters.repositories.stream import MongoStreamRepository
from api.deps.mongo import get_db
from domain.interfaces import IStreamRepository, StreamQuery

if TYPE_CHECKING:
    from domain.models import StreamWithRelations


def get_stream_repo(
    db: AsyncIOMotorClient = Depends(get_db),
) -> IStreamRepository:
    return MongoStreamRepository(db)


async def get_by_slug(
    slug: str,
    streams: IStreamRepository = Depends(get_stream_repo),
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


async def get_stream_fetcher(
    db: AsyncIOMotorClient = Depends(get_db),
) -> StreamFetcher:
    return MongoStreamFetcher(db)
