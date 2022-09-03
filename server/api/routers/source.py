from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel

from api.deps.source import get_source_by_slug, get_source_repo
from api.routers.core import ListResponse
from domain.interfaces import AbstractSourceRepository
from domain.models import Source as SourceModel

router = APIRouter()


class Source(BaseModel):
    name: str
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


@router.get("/sources", response_model=Sources)
async def get_sources(
    sources: AbstractSourceRepository = Depends(get_source_repo),
) -> ListResponse:
    return ListResponse(
        count=await sources.get_sources_count(),
        page=1,
        results=await sources.get_sources(),
    )


@router.post("/sources", response_model=Source, status_code=201)
async def add_source(
    source: Source = Body(),
    sources: AbstractSourceRepository = Depends(get_source_repo),
) -> SourceModel:
    await sources.add_source(source.to_domain())
    result = await sources.get_source_by_slug(source.slug)
    # TODO https://stackoverflow.com/a/68552742
    assert isinstance(result, SourceModel)  # noqa S101
    return result


@router.get("/sources/{slug}", response_model=Source)
async def get_source(
    source: SourceModel = Depends(get_source_by_slug),
) -> SourceModel:
    return source
