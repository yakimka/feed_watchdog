from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.repositories.receiver import MongoReceiverRepository
from api.deps.mongo import get_db
from domain.interfaces import IReceiverRepository


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
