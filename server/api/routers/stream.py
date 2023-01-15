from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from api.deps.pagination import Pagination, get_pagination_params
from api.deps.stream import (
    StreamFetcher,
    get_by_slug,
    get_stream_fetcher,
    get_stream_repo,
)
from api.deps.user import get_current_user
from api.routers.core import ListResponse
from domain.interfaces import IStreamRepository, StreamQuery
from domain.models import Stream as StreamModel

router = APIRouter(dependencies=[Depends(get_current_user)])


class Modifier(BaseModel):
    type: str
    options: dict


class Stream(BaseModel):
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


class SourceInStream(BaseModel):
    name: str
    slug: str


class ReceiverInStream(BaseModel):
    name: str
    slug: str


class StreamInList(BaseModel):
    slug: str
    source: SourceInStream
    receiver: ReceiverInStream
    intervals: list[str]
    active: bool


class Streams(ListResponse):
    results: list[StreamInList]


@router.get("/streams", response_model=Streams)
async def find(
    fetcher: StreamFetcher = Depends(get_stream_fetcher),
    q: str = "",
    pagination: Pagination = Depends(get_pagination_params),
) -> ListResponse:
    query = StreamQuery(
        search=q,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return ListResponse(
        count=await fetcher.get_count(query),
        page=1,
        results=await fetcher.search(query),
        page_size=pagination.page_size,
    )


@router.post("/streams", response_model=Stream, status_code=201)
async def add(
    stream: Stream = Body(),
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
    stream: Stream = Body(),
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
