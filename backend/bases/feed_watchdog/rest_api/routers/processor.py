from fastapi import APIRouter, Depends
from picodi import Provide, inject

from feed_watchdog.domain.interfaces import IProcessorsConfigurationRepository
from feed_watchdog.rest_api.dependencies import get_processors_conf_repository
from feed_watchdog.rest_api.deps.user import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/processors/config/{handler}/")
@inject
def get_handler_config(
    handler: str,
    processors_conf: IProcessorsConfigurationRepository = Depends(
        Provide(get_processors_conf_repository)
    ),
) -> dict:
    return processors_conf.get_config(handler)
