from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


class FieldError(BaseModel):
    message: str
    field: str


class ErrorResponse(BaseModel):
    type: str
    message: str
    details: list[FieldError]

    @classmethod
    def from_validation_error(cls, error: RequestValidationError):
        errors = error.errors()
        first_error = errors[0]
        response = cls(
            type=first_error["type"], message=first_error["msg"], details=[]
        )
        for error in errors:
            if error["type"] != response.type:
                continue

            response.details.append(
                FieldError(
                    field=".".join(error["loc"][1:]), message=error["msg"]
                )
            )
        return response

    def to_response(self):
        return {"error": self.dict()}
