from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

from db import models as django_models

if TYPE_CHECKING:
    from domain.models import Stream


class StreamRepository:
    def list(self, cron_interval: str = "") -> Generator[Stream, None, None]:
        filters: dict[str, Any] = {"active": True}
        if cron_interval:
            filters["intervals__cron"] = cron_interval

        for stream in django_models.Stream.objects.filter(**filters):
            yield stream.to_domain()
