from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.repositories.stream import MongoStreamRepository
from api.deps.mongo import get_db
from domain.interfaces import IStreamRepository


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
