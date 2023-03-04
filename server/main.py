from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from adapters import sentry
from api.errors import ErrorResponse, FieldError
from api.exceptions import ValueExistsError
from api.routers import router
from container import container, wire_modules

wire_modules()

sentry.setup_fastapi(container.settings().sentry.dsn)

app = FastAPI()
app.include_router(router)

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueExistsError)
async def http_exception_handler(request, exc):  # noqa: PLW0613
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            type="duplicate_key",
            message="Object with duplicated value detected",
            details=[
                FieldError(field=exc.field, message=exc.message),
            ],
        ).to_response(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):  # noqa: PLW0613
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.from_validation_error(exc).to_response(),
    )
