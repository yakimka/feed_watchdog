from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from feed_watchdog.domain.interfaces import ISourceRepository
from feed_watchdog.repositories.source import MongoSourceRepository
from feed_watchdog.rest_api.deps.mongo import get_db


def get_source_repo(
    db: AsyncIOMotorClient = Depends(get_db),
) -> ISourceRepository:
    return MongoSourceRepository(db)


async def get_by_slug(
    slug: str,
    sources: ISourceRepository = Depends(get_source_repo),
):
    source = await sources.get_by_slug(slug)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
