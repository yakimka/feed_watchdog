from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from feed_watchdog.domain.interfaces import IReceiverRepository
from feed_watchdog.repositories.receiver import MongoReceiverRepository
from feed_watchdog.rest_api.deps.mongo import get_db


def get_receiver_repo(
    db: AsyncIOMotorClient = Depends(get_db),
) -> IReceiverRepository:
    return MongoReceiverRepository(db)


async def get_by_slug(
    slug: str,
    receivers: IReceiverRepository = Depends(get_receiver_repo),
):
    receiver = await receivers.get_by_slug(slug)
    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return receiver
