from dependency_injector.wiring import Provide, inject
from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from feed_watchdog.rest_api.container import Container


@inject
def get_db(
    client: AsyncIOMotorClient = Depends(Provide[Container.mongo_client]),
):
    return client.get_database()


# uvicorn feed_watchdog.rest_api.core:app --host 0.0.0.0 --port 8000
