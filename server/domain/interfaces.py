import abc
from abc import abstractmethod

from pydantic import BaseModel

from domain.models import Receiver, Source, Stream, UserInDB


class PaginationQuery(BaseModel):
    page: int = 1
    page_size: int = 100


class SourceQuery(PaginationQuery):
    search: str = ""
    sort_by: str = "name"


class ReceiverQuery(PaginationQuery):
    search: str = ""
    sort_by: str = "name"


class StreamQuery(PaginationQuery):
    search: str = ""
    sort_by: str = "name"


class ISourceRepository(abc.ABC):
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


class IReceiverRepository(abc.ABC):
    @abstractmethod
    async def find(
        self, query: ReceiverQuery = ReceiverQuery()
    ) -> list[Receiver]:
        pass

    @abstractmethod
    async def get_count(self, query: ReceiverQuery = ReceiverQuery()) -> int:
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


class IStreamRepository(abc.ABC):
    @abstractmethod
    async def find(self, query: StreamQuery = StreamQuery()) -> list[Stream]:
        pass

    @abstractmethod
    async def get_count(self, query: StreamQuery = StreamQuery()) -> int:
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


class IProcessorsConfigurationRepository(abc.ABC):
    @abstractmethod
    def get_config(self, handler: str) -> dict:
        pass


class IUserRepository(abc.ABC):
    @abstractmethod
    async def get_user_by_id(self, id: str) -> UserInDB | None:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserInDB | None:
        pass

    @abstractmethod
    async def create_user(self, user: UserInDB) -> None:
        pass
