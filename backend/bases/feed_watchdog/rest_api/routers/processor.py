from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from feed_watchdog.domain.interfaces import IProcessorsConfigurationRepository
from feed_watchdog.rest_api.container import Container
from feed_watchdog.rest_api.deps.user import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/processors/config/{handler}/")
@inject
def get_handler_config(
    handler: str,
    processors_conf: IProcessorsConfigurationRepository = Depends(
        Provide[Container.processors_conf_repository]
    ),
) -> dict:
    return processors_conf.get_config(handler)
