import argparse
import asyncio
import inspect
import logging
from pathlib import Path

import picodi
from picodi import Provide

from feed_watchdog.commands.core import parse_command_and_args
from feed_watchdog.handlers import init_handlers_config
from feed_watchdog.sentry.setup import setup_logging as setup_sentry_logging
from feed_watchdog.workers.settings import Settings, get_settings

CURR_DIR = Path(__file__).parent


def main() -> None:
    setup()
    parser = argparse.ArgumentParser()
    worker, args = parse_command_and_args(
        parser=parser,
        path_to_commands=CURR_DIR / "workers",
        import_path="feed_watchdog.workers.workers",
        dest="worker",
    )
    if inspect.iscoroutinefunction(worker.handle):

        async def run_worker() -> None:
            await picodi.init_resources()
            try:
                await worker.handle(args)  # type: ignore[misc]
            finally:
                await picodi.shutdown_resources()

        asyncio.run(run_worker())
    else:
        picodi.init_resources()
        try:
            worker.handle(args)
        finally:
            picodi.shutdown_resources()


def setup(settings: Settings = Provide(get_settings)) -> None:
    setup_sentry_logging(settings.sentry.dsn)
    init_handlers_config(settings.app.handlers_conf_path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


if __name__ == "__main__":
    main()
