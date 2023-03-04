from dependency_injector.wiring import Provide, inject
from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from container import Container


@inject
def get_db(
    client: AsyncIOMotorClient = Depends(Provide[Container.mongo_client]),
):
    return client.get_database()
