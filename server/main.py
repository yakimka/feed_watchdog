from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from api.errors import APIError
from api.exceptions import ValueExistsError
from api.routers import router

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
        content={
            "detail": APIError(message=exc.message, field=exc.field).dict()
        },
    )
