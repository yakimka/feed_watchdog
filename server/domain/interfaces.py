from abc import abstractmethod

from pydantic import BaseModel

from domain.models import Receiver, Source, Stream


class SourceQuery(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 100
    sort_by: str = "name"


class ISourceRepository:
    @abstractmethod
    async def find(self, query: SourceQuery = SourceQuery()) -> list[Source]:
        pass

    @abstractmethod
    async def get_count(self, query: SourceQuery = SourceQuery()) -> int:
        pass

    @abstractmethod
    async def add(self, source: Source) -> str:
        pass

    @abstractmethod
    async def update(self, slug: str, source: Source) -> bool:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Source | None:
        pass

    @abstractmethod
    async def delete_by_slug(self, slug: str) -> bool:
        pass


class IReceiverRepository:
    @abstractmethod
    async def find(self) -> list[Receiver]:
        pass

    @abstractmethod
    async def get_count(self) -> int:
        pass

    @abstractmethod
    async def add(self, receiver: Receiver) -> str:
        pass

    @abstractmethod
    async def update(self, slug: str, receiver: Receiver) -> None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Receiver | None:
        pass

    @abstractmethod
    async def delete_by_slug(self, slug: str) -> None:
        pass


class IStreamRepository:
    @abstractmethod
    async def find(self) -> list[Stream]:
        pass

    @abstractmethod
    async def get_count(self) -> int:
        pass

    @abstractmethod
    async def add(self, stream: Stream) -> str:
        pass

    @abstractmethod
    async def update(self, slug: str, stream: Stream) -> None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Stream | None:
        pass

    @abstractmethod
    async def delete_by_slug(self, slug: str) -> None:
        pass
