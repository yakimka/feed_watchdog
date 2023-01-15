from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from api.deps.pagination import Pagination, get_pagination_params
from api.deps.receiver import get_by_slug, get_receiver_repo
from api.deps.user import get_current_user
from api.routers.core import ListResponse
from domain.interfaces import IReceiverRepository, ReceiverQuery
from domain.models import Receiver as ReceiverModel

router = APIRouter(dependencies=[Depends(get_current_user)])


class Receiver(BaseModel):
    name: str
    slug: str
    type: str
    options: dict
    options_allowed_to_override: list[str] = []

    def to_domain(self) -> ReceiverModel:
        return ReceiverModel.parse_obj(self.dict())


class Receivers(ListResponse):
    results: list[Receiver]


@router.get("/receivers", response_model=Receivers)
async def find(
    receivers: IReceiverRepository = Depends(get_receiver_repo),
    q: str = "",
    pagination: Pagination = Depends(get_pagination_params),
) -> ListResponse:
    query = ReceiverQuery(
        search=q,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return ListResponse(
        count=await receivers.get_count(query),
        page=1,
        results=await receivers.find(query),
        page_size=pagination.page_size,
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
