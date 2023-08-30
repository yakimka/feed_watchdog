from dependency_injector.wiring import Provide, inject

from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.migrations.mongo import migrate
from feed_watchdog.rest_api.container import Container
from feed_watchdog.rest_api.settings import Settings


class MigrateCommand(BaseCommand):
    @inject
    def setup(
        self,
        settings: Settings = Provide[Container.settings],
    ) -> None:
        self._settings = settings

    def handle(self, args):  # noqa: U100
        migrate(self._settings.mongo.url)
