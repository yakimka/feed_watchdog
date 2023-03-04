from pydantic import BaseModel, root_validator


class ListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    results: list
    pages: int = 0

    @root_validator
    def compute_pages(cls, values) -> dict:
        if not values["pages"]:
            values["pages"] = values["count"] // values["page_size"]

        return values
