from pydantic import BaseModel


class APIError(BaseModel):
    message: str
    field: str | None = None
