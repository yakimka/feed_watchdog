import argparse
import logging
from pathlib import Path

from feed_watchdog.commands.core import parse_command_and_args
from feed_watchdog.handlers import init_handlers_config
from feed_watchdog.sentry.setup import setup_logging as setup_sentry_logging
from feed_watchdog.workers.container import container, wire_modules

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
    worker.handle(args)


def setup() -> None:
    wire_modules()
    settings = container.settings()
    setup_sentry_logging(settings.sentry.dsn)
    init_handlers_config(settings.app.handlers_conf_path)

    logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    main()
