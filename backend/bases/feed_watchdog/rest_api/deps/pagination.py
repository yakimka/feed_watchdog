from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    page_size: int


def get_pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
) -> Pagination:
    return Pagination(page=page, page_size=page_size)
