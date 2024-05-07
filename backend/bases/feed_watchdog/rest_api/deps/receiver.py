from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from picodi import Provide, inject

from feed_watchdog.domain.interfaces import IReceiverRepository
from feed_watchdog.repositories.receiver import MongoReceiverRepository
from feed_watchdog.rest_api.dependencies import get_mongo_db


@inject
def get_receiver_repo(
    db: AsyncIOMotorClient = Provide(get_mongo_db),
) -> IReceiverRepository:
    return MongoReceiverRepository(db)


@inject
async def get_by_slug(
    slug: str,
    receivers: IReceiverRepository = Provide(get_receiver_repo),
):
    receiver = await receivers.get_by_slug(slug)
    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return receiver
