from fastapi import HTTPException
from picodi import inject
from picodi.integrations.fastapi import Provide

from feed_watchdog.domain.interfaces import IReceiverRepository
from feed_watchdog.rest_api.dependencies import get_receiver_repository


@inject
async def get_by_slug(
    slug: str,
    receivers: IReceiverRepository = Provide(get_receiver_repository, wrap=True),
):
    receiver = await receivers.get_by_slug(slug)
    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return receiver
