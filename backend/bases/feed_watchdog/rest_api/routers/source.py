from fastapi import APIRouter, Body, Depends, HTTPException
from picodi import inject
from picodi.integrations.fastapi import Provide
from pydantic import BaseModel, Field

from feed_watchdog.domain.interfaces import (
    ISourceRepository,
    IStreamRepository,
    SourceQuery,
)
from feed_watchdog.domain.models import Source as SourceModel
from feed_watchdog.rest_api.dependencies import (
    get_source_repository,
    get_stream_repository,
)
from feed_watchdog.rest_api.deps.pagination import Pagination, get_pagination_params
from feed_watchdog.rest_api.deps.source import get_by_slug
from feed_watchdog.rest_api.deps.user import get_current_user
from feed_watchdog.rest_api.routers.core import ListResponse

router = APIRouter(dependencies=[Depends(get_current_user)])


class Source(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str = ""
    tags: tuple | list = ()

    def to_domain(self) -> SourceModel:
        return SourceModel.parse_obj(self.dict())


class Sources(ListResponse):
    results: list[Source]


@router.get("/sources/", response_model=Sources)
@inject
async def find(
    sources: ISourceRepository = Provide(get_source_repository, wrap=True),
    q: str = "",
    pagination: Pagination = Depends(get_pagination_params),
) -> ListResponse:
    query = SourceQuery(
        search=q,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return ListResponse(
        count=await sources.get_count(query),
        page=1,
        results=await sources.find(query),
        page_size=pagination.page_size,
    )


@router.get("/sources/tags/", response_model=list[str])
@inject
async def tags(
    sources: ISourceRepository = Provide(get_source_repository, wrap=True),
) -> list[str]:
    return await sources.get_all_tags()


@router.post("/sources/", response_model=Source, status_code=201)
@inject
async def add(
    source: Source = Body(),
    sources: ISourceRepository = Provide(get_source_repository, wrap=True),
) -> SourceModel:
    await sources.add(source.to_domain())
    result = await sources.get_by_slug(source.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, SourceModel)  # S101
    return result


@router.put("/sources/{slug}/", response_model=Source, status_code=201)
@inject
async def update(
    slug: str,
    source: Source = Body(),
    sources: ISourceRepository = Provide(get_source_repository, wrap=True),
) -> SourceModel:
    updated = await sources.update(slug, source.to_domain())
    if not updated:
        raise HTTPException(status_code=404, detail="Source not found")

    result = await sources.get_by_slug(source.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, SourceModel)  # S101
    return result


@router.get("/sources/{slug}/", response_model=Source)
@inject
async def detail(
    source: SourceModel = Depends(get_by_slug),
) -> SourceModel:
    return source


@router.delete("/sources/{slug}/", response_model=None, status_code=204)
@inject
async def delete(
    source: SourceModel = Depends(get_by_slug),
    sources: ISourceRepository = Provide(get_source_repository, wrap=True),
    streams: IStreamRepository = Provide(get_stream_repository, wrap=True),
) -> None:
    if await streams.get_by_source_slug(source.slug):
        raise HTTPException(status_code=409, detail="Source is in use")

    deleted = await sources.delete(source)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return None
