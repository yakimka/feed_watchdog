from fastapi import APIRouter, Depends

from feed_watchdog.domain.interfaces import IProcessorsConfigurationRepository
from feed_watchdog.rest_api.deps.processor import get_processors_conf_repo
from feed_watchdog.rest_api.deps.user import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/processors/config/{handler}/")
def get_handler_config(
    handler: str,
    processors_conf: IProcessorsConfigurationRepository = Depends(
        get_processors_conf_repo
    ),
) -> dict:
    return processors_conf.get_config(handler)
