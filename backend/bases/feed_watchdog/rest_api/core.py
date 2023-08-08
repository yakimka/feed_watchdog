from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from feed_watchdog.repositories.exceptions import ValueExistsError
from feed_watchdog.rest_api.container import container, wire_modules
from feed_watchdog.rest_api.errors import ErrorResponse, FieldError
from feed_watchdog.rest_api.routers import router
from feed_watchdog.sentry import setup as setup_sentry

wire_modules()

setup_sentry.setup_fastapi(container.settings().sentry.dsn)

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
async def http_exception_handler(request, exc):  # noqa: U100
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
async def validation_exception_handler(request, exc):  # noqa: U100
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.from_validation_error(exc).to_response(),
    )