import argparse
import asyncio
import inspect
import logging
from pathlib import Path

import picodi
from picodi import Provide, inject

from feed_watchdog.commands.core import choose_and_setup_command, find_commands_in_dir
from feed_watchdog.handlers import init_handlers_config
from feed_watchdog.sentry.setup import setup_logging as setup_sentry_logging
from feed_watchdog.workers.dependencies import init_lock
from feed_watchdog.workers.settings import Settings, get_settings

CURR_DIR = Path(__file__).parent


async def main() -> None:
    setup()
    commands = list(
        find_commands_in_dir(
            path_to_commands=CURR_DIR / "workers",
            import_path="feed_watchdog.workers.workers",
        )
    )
    await picodi.init_dependencies()
    await init_lock()

    parser = argparse.ArgumentParser()
    worker, args = choose_and_setup_command(
        parser=parser,
        commands_to_setup=commands,
        dest="worker",
    )
    try:
        result = worker.handle(args)
        if inspect.isawaitable(result):
            await result
    finally:
        await picodi.shutdown_dependencies()


@inject
def setup(settings: Settings = Provide(get_settings)) -> None:
    setup_sentry_logging(settings.sentry.dsn)
    init_handlers_config(settings.app.handlers_conf_path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


if __name__ == "__main__":
    asyncio.run(main())
