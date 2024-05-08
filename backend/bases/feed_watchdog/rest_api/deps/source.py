from fastapi import Depends, HTTPException
from picodi import Provide, inject

from feed_watchdog.domain.interfaces import ISourceRepository
from feed_watchdog.rest_api.dependencies import get_source_repository


@inject
async def get_by_slug(
    slug: str,
    sources: ISourceRepository = Depends(Provide(get_source_repository)),
):
    source = await sources.get_by_slug(slug)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
