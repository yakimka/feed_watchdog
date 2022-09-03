from fastapi import APIRouter

from api.routers import source

router = APIRouter()

api_router = APIRouter(prefix="/api")
api_router.include_router(source.router, tags=["source"])

router.include_router(api_router)
