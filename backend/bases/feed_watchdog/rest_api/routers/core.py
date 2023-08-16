from pydantic import BaseModel, model_validator


class ListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    results: list
    pages: int = 0

    @model_validator(mode="after")
    def compute_pages(self):
        if not self.pages:
            self.pages = self.count // self.page_size

        return self
