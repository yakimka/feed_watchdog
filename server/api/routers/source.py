from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps.pagination import Pagination, get_pagination_params
from api.deps.source import get_by_slug, get_source_repo
from api.deps.user import get_current_user
from api.routers.core import ListResponse
from domain.interfaces import ISourceRepository, SourceQuery
from domain.models import Source as SourceModel

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
async def find(
    sources: ISourceRepository = Depends(get_source_repo),
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
async def tags(
    sources: ISourceRepository = Depends(get_source_repo),
) -> list[str]:
    return await sources.get_all_tags()


@router.post("/sources/", response_model=Source, status_code=201)
async def add(
    source: Source = Body(),
    sources: ISourceRepository = Depends(get_source_repo),
) -> SourceModel:
    await sources.add(source.to_domain())
    result = await sources.get_by_slug(source.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, SourceModel)  # noqa S101
    return result


@router.put("/sources/{slug}/", response_model=Source, status_code=201)
async def update(
    slug: str,
    source: Source = Body(),
    sources: ISourceRepository = Depends(get_source_repo),
) -> SourceModel:
    updated = await sources.update(slug, source.to_domain())
    if not updated:
        raise HTTPException(status_code=404, detail="Source not found")

    result = await sources.get_by_slug(source.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, SourceModel)  # noqa S101
    return result


@router.get("/sources/{slug}/", response_model=Source)
async def detail(
    source: SourceModel = Depends(get_by_slug),
) -> SourceModel:
    return source


@router.delete("/sources/{slug}/", status_code=204)
async def delete(
    slug: str,
    sources: ISourceRepository = Depends(get_source_repo),
) -> str:
    deleted = await sources.delete_by_slug(slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return ""
