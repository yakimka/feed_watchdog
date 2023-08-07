import abc
from abc import abstractmethod

from pydantic import BaseModel

from feed_watchdog.domain.models import (
    Receiver,
    RefreshToken,
    Source,
    Stream,
    UserInDB,
)


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
    interval: str | None = None
    only_active: bool = False
    sort_by: str = "name"


class ISourceRepository(abc.ABC):
    @abstractmethod
    async def find(self, query: SourceQuery) -> list[Source]:
        pass

    @abstractmethod
    async def get_count(self, query: SourceQuery) -> int:
        pass

    @abstractmethod
    async def get_all_tags(self) -> list[str]:
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
    async def delete(self, source: Source) -> bool:
        pass


class IReceiverRepository(abc.ABC):
    @abstractmethod
    async def find(self, query: ReceiverQuery) -> list[Receiver]:
        pass

    @abstractmethod
    async def get_count(self, query: ReceiverQuery) -> int:
        pass

    @abstractmethod
    async def add(self, receiver: Receiver) -> str:
        pass

    @abstractmethod
    async def update(self, slug: str, receiver: Receiver) -> bool:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Receiver | None:
        pass

    @abstractmethod
    async def delete(self, receiver: Receiver) -> bool:
        pass


class IStreamRepository(abc.ABC):
    @abstractmethod
    async def find(self, query: StreamQuery) -> list[Stream]:
        pass

    @abstractmethod
    async def get_count(self, query: StreamQuery) -> int:
        pass

    @abstractmethod
    async def add(self, stream: Stream) -> str:
        pass

    @abstractmethod
    async def update(self, slug: str, stream: Stream) -> bool:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Stream | None:
        pass

    @abstractmethod
    async def get_by_source_slug(self, source_slug: str) -> list[Stream]:
        pass

    @abstractmethod
    async def get_by_receiver_slug(self, receiver_slug: str) -> list[Stream]:
        pass

    @abstractmethod
    async def delete_by_slug(self, slug: str) -> bool:
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
    async def create_user(self, user: UserInDB) -> str:
        pass


class IRefreshTokenRepository(abc.ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[RefreshToken]:
        pass

    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> str:
        pass

    @abstractmethod
    async def delete(self, token: str) -> bool:
        pass

    @abstractmethod
    async def delete_all(self, user_id: str) -> bool:
        pass


class IPostRepository:
    async def sent_posts_count(self, stream_id: str, receiver_type: str) -> int:
        pass

    async def post_was_sent(
        self, post_id: str, stream_id: str, receiver_type: str
    ) -> bool:
        pass

    async def save_post_sent_flag(
        self, post_id: str, stream_id: str, receiver_type: str
    ) -> None:
        pass
