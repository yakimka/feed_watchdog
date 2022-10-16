from fastapi import APIRouter

from api.routers import processor, receiver, source, stream

router = APIRouter()

api_router = APIRouter(prefix="/api")
api_router.include_router(source.router, tags=["Source"])
api_router.include_router(receiver.router, tags=["Receiver"])
api_router.include_router(stream.router, tags=["Stream"])
api_router.include_router(processor.router, tags=["Processor"])

router.include_router(api_router)
