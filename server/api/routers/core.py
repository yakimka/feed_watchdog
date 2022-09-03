from pydantic import BaseModel


class ListResponse(BaseModel):
    count: int
    page: int
    results: list
