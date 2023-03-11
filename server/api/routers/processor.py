from fastapi import APIRouter, Depends

from api.deps.processor import get_processors_conf_repo
from api.deps.user import get_current_user
from domain.interfaces import IProcessorsConfigurationRepository

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/processors/config/{handler}/")
def get_handler_config(
    handler: str,
    processors_conf: IProcessorsConfigurationRepository = Depends(
        get_processors_conf_repo
    ),
) -> dict:
    return processors_conf.get_config(handler)
