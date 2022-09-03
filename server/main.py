from fastapi import FastAPI
from starlette.responses import JSONResponse

from api.errors import APIError
from api.exceptions import ValueExistsError
from api.routers import router

app = FastAPI()
app.include_router(router)


@app.exception_handler(ValueExistsError)
async def http_exception_handler(request, exc):  # noqa: PLW0613
    return JSONResponse(
        status_code=400,
        content={
            "detail": APIError(message=exc.message, field=exc.field).dict()
        },
    )
