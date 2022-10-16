from adapters.repositories.processor import FileProcessorsConfigRepo
from domain.interfaces import IProcessorsConfigurationRepository


def get_processors_conf_repo() -> IProcessorsConfigurationRepository:
    return FileProcessorsConfigRepo("/app/handlers.json")
