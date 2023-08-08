from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel

from feed_watchdog.domain.interfaces import IStreamRepository, StreamQuery
from feed_watchdog.domain.models import Stream, StreamWithRelations
from feed_watchdog.rest_api.container import Container
from feed_watchdog.rest_api.deps.pagination import (
    Pagination,
    get_pagination_params,
)
from feed_watchdog.rest_api.deps.stream import (
    StreamFetcher,
    get_by_slug,
    get_stream_fetcher,
    get_stream_repo,
)
from feed_watchdog.rest_api.deps.user import get_current_user
from feed_watchdog.rest_api.routers.core import ListResponse

router = APIRouter(dependencies=[Depends(get_current_user)])


class ModifierResp(BaseModel):
    type: str
    options: dict


class BaseStream(BaseModel):
    slug: str
    intervals: list[str]
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[ModifierResp]
    active: bool


class StreamBody(BaseStream):
    source_slug: str
    receiver_slug: str

    def to_internal(self) -> Stream:
        return Stream.parse_obj(self.dict())


class StreamResp(BaseStream):
    source_slug: str
    receiver_slug: str


class SourceResp(BaseModel):
    name: str
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str
    tags: list


class ReceiverResp(BaseModel):
    name: str
    slug: str
    type: str
    options: dict
    options_allowed_to_override: list[str]


class StreamExtendedResp(BaseStream):
    source: SourceResp
    receiver: ReceiverResp

    @classmethod
    def from_domain(cls, stream: StreamWithRelations):
        return cls.parse_obj(stream.dict())


class StreamListResp(ListResponse):
    results: list[StreamExtendedResp]


@router.get("/streams/", response_model=StreamListResp)
async def find(
    fetcher: StreamFetcher = Depends(get_stream_fetcher),
    pagination: Pagination = Depends(get_pagination_params),
    q: str = "",
    interval: str | None = Query(None),
    only_active: bool = False,
) -> ListResponse:
    query = StreamQuery(
        search=q,
        interval=interval,
        only_active=only_active,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return ListResponse(
        count=await fetcher.get_count(query),
        page=1,
        results=[
            StreamExtendedResp.from_domain(item)
            for item in await fetcher.search(query)
        ],
        page_size=pagination.page_size,
    )


@router.get("/streams/intervals/")
@inject
async def get_intervals(
    intervals=Depends(Provide[Container.config.app.intervals]),
) -> list[dict]:
    return intervals


@router.get("/streams/message_templates/")
@inject
async def get_message_templates(
    intervals=Depends(Provide[Container.config.app.message_templates]),
) -> list[dict]:
    return intervals


@router.post("/streams/", response_model=StreamResp, status_code=201)
async def add(
    stream: StreamBody = Body(),
    streams: IStreamRepository = Depends(get_stream_repo),
) -> Stream:
    await streams.add(stream.to_internal())
    result = await streams.get_by_slug(stream.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, Stream)  # S101
    return result


@router.put("/streams/{slug}/", response_model=StreamResp, status_code=201)
async def update(
    slug: str,
    stream: StreamBody = Body(),
    streams: IStreamRepository = Depends(get_stream_repo),
) -> Stream:
    updated = await streams.update(slug, stream.to_internal())
    if not updated:
        raise HTTPException(status_code=404, detail="Stream not found")

    result = await streams.get_by_slug(stream.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, Stream)  # S101
    return result


@router.get("/streams/{slug}/", response_model=StreamResp)
async def detail(
    stream: Stream = Depends(get_by_slug),
) -> Stream:
    return stream


@router.delete("/streams/{slug}/", response_model=None, status_code=204)
async def delete(
    slug: str,
    streams: IStreamRepository = Depends(get_stream_repo),
) -> None:
    deleted = await streams.delete_by_slug(slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stream not found")
    return None