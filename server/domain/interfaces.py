from abc import abstractmethod

from domain.models import Source


class AbstractSourceRepository:
    @abstractmethod
    async def get_sources(self) -> list[Source]:
        pass

    @abstractmethod
    async def get_sources_count(self) -> int:
        pass

    @abstractmethod
    async def add_source(self, source: Source) -> str:
        pass

    @abstractmethod
    async def get_source_by_slug(self, slug: str) -> Source | None:
        pass
