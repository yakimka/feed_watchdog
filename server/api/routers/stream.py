from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from api.deps.pagination import Pagination, get_pagination_params
from api.deps.stream import get_by_slug, get_stream_repo
from api.routers.core import ListResponse
from domain.interfaces import IStreamRepository, StreamQuery
from domain.models import Stream as StreamModel

router = APIRouter()


class Modifier(BaseModel):
    type: str
    options: dict


class SourceInStream(BaseModel):
    name: str
    slug: str


class ReceiverInStream(BaseModel):
    name: str
    slug: str


class StreamForCreate(BaseModel):
    slug: str
    source_slug: str
    receiver_slug: str
    intervals: list[str]
    squash: bool
    receiver_options_override: dict = {}
    message_template: str
    modifiers: list[Modifier] = []
    active: bool

    def to_domain(self) -> StreamModel:
        return StreamModel.parse_obj(self.dict())


class Stream(StreamForCreate):
    def to_domain(self) -> StreamModel:
        return StreamModel.parse_obj(self.dict())


class Streams(ListResponse):
    results: list[Stream]


@router.get("/streams", response_model=Streams)
async def find(
    streams: IStreamRepository = Depends(get_stream_repo),
    q: str = "",
    pagination: Pagination = Depends(get_pagination_params),
) -> ListResponse:
    query = StreamQuery(
        search=q,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return ListResponse(
        count=await streams.get_count(query),
        page=1,
        results=await streams.find(query),
        page_size=pagination.page_size,
    )


@router.post("/streams", response_model=Stream, status_code=201)
async def add(
    stream: StreamForCreate = Body(),
    streams: IStreamRepository = Depends(get_stream_repo),
) -> StreamModel:
    await streams.add(stream.to_domain())
    result = await streams.get_by_slug(stream.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, StreamModel)  # noqa S101
    return result


@router.put("/streams/{slug}", response_model=Stream, status_code=201)
async def update(
    slug: str,
    stream: StreamForCreate = Body(),
    streams: IStreamRepository = Depends(get_stream_repo),
) -> StreamModel:
    updated = await streams.update(slug, stream.to_domain())
    if not updated:
        raise HTTPException(status_code=404, detail="Stream not found")

    result = await streams.get_by_slug(stream.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, StreamModel)  # noqa S101
    return result


@router.get("/streams/{slug}", response_model=Stream)
async def detail(
    stream: StreamModel = Depends(get_by_slug),
) -> StreamModel:
    return stream


@router.delete("/streams/{slug}", status_code=204)
async def delete(
    slug: str,
    streams: IStreamRepository = Depends(get_stream_repo),
) -> str:
    deleted = await streams.delete_by_slug(slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stream not found")
    return ""
