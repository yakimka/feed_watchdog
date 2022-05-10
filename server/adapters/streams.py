from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from db import models as django_models

if TYPE_CHECKING:
    from domain.models import Stream


class StreamRepository:
    def list(self) -> Generator[Stream, None, None]:
        for stream in django_models.Stream.objects.filter(active=True):
            yield stream.to_domain()
