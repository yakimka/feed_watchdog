from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from picodi import Provide, inject

from feed_watchdog.domain.interfaces import ISourceRepository
from feed_watchdog.repositories.source import MongoSourceRepository
from feed_watchdog.rest_api.dependencies import get_mongo_db


@inject
def get_source_repo(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> ISourceRepository:
    return MongoSourceRepository(db)


@inject
async def get_by_slug(
    slug: str,
    sources: ISourceRepository = Provide(get_source_repo),
):
    source = await sources.get_by_slug(slug)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
