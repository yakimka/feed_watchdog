from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from api.deps.receiver import get_by_slug, get_receiver_repo
from api.routers.core import ListResponse
from domain.interfaces import IReceiverRepository
from domain.models import Receiver as ReceiverModel

router = APIRouter()


class Receiver(BaseModel):
    name: str
    slug: str
    type: str
    options: dict

    def to_domain(self) -> ReceiverModel:
        return ReceiverModel.parse_obj(self.dict())


class Receivers(ListResponse):
    results: list[Receiver]


@router.get("/receivers", response_model=Receivers)
async def find(
    receivers: IReceiverRepository = Depends(get_receiver_repo),
) -> ListResponse:
    return ListResponse(
        count=await receivers.get_count(),
        page=1,
        results=await receivers.find(),
    )


@router.post("/receivers", response_model=Receiver, status_code=201)
async def add(
    receiver: Receiver = Body(),
    receivers: IReceiverRepository = Depends(get_receiver_repo),
) -> ReceiverModel:
    await receivers.add(receiver.to_domain())
    result = await receivers.get_by_slug(receiver.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, ReceiverModel)  # noqa S101
    return result


@router.put("/receivers/{slug}", response_model=Receiver, status_code=201)
async def update(
    slug: str,
    receiver: Receiver = Body(),
    receivers: IReceiverRepository = Depends(get_receiver_repo),
) -> ReceiverModel:
    updated = await receivers.update(slug, receiver.to_domain())
    if not updated:
        raise HTTPException(status_code=404, detail="Receiver not found")

    result = await receivers.get_by_slug(receiver.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, ReceiverModel)  # noqa S101
    return result


@router.get("/receivers/{slug}", response_model=Receiver)
async def detail(
    receiver: ReceiverModel = Depends(get_by_slug),
) -> ReceiverModel:
    return receiver


@router.delete("/receivers/{slug}", status_code=204)
async def delete(
    slug: str,
    receivers: IReceiverRepository = Depends(get_receiver_repo),
) -> str:
    deleted = await receivers.delete_by_slug(slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return ""
