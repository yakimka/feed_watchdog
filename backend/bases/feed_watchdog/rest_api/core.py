from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from picodi import picodi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics

from feed_watchdog.repositories.exceptions import ValueExistsError
from feed_watchdog.rest_api.errors import ErrorResponse, FieldError
from feed_watchdog.rest_api.routers import router
from feed_watchdog.rest_api.settings import get_settings
from feed_watchdog.sentry import setup as setup_sentry

settings = get_settings()
setup_sentry.setup_fastapi(settings.sentry.dsn)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: U100
    await picodi.init_resources()
    yield
    await picodi.shutdown_resources()


app = FastAPI(lifespan=lifespan)
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
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


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
