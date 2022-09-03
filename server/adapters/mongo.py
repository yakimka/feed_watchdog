from motor.motor_asyncio import AsyncIOMotorClient


def get_client() -> AsyncIOMotorClient:
    # TODO from settings
    return AsyncIOMotorClient("mongodb://mongo:27017")
