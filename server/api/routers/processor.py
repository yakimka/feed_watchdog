from fastapi import APIRouter, Depends

from api.deps.processor import get_processors_conf_repo
from domain.interfaces import IProcessorsConfigurationRepository

router = APIRouter()


@router.get("/processors/config/{handler}")
def get_handler_config(
    handler: str,
    processors_conf: IProcessorsConfigurationRepository = Depends(
        get_processors_conf_repo
    ),
) -> dict:
    return processors_conf.get_config(handler)
