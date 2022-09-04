from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from api.deps.stream import get_by_slug, get_stream_repo
from api.routers.core import ListResponse
from domain.interfaces import IStreamRepository
from domain.models import Stream as StreamModel

router = APIRouter()


class Modifier(BaseModel):
    type: str
    options: dict


class Source(BaseModel):
    name: str
    slug: str


class Receiver(BaseModel):
    name: str
    slug: str


class Stream(BaseModel):
    stream: Source
    receiver: Receiver
    slug: str
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[Modifier] = []

    def to_domain(self) -> StreamModel:
        return StreamModel.parse_obj(self.dict())


class Streams(ListResponse):
    results: list[Stream]


@router.get("/streams", response_model=Streams)
async def find(
    streams: IStreamRepository = Depends(get_stream_repo),
) -> ListResponse:
    return ListResponse(
        count=await streams.get_count(),
        page=1,
        results=await streams.find(),
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
