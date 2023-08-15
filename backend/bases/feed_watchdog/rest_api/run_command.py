import argparse
import logging
from pathlib import Path

from feed_watchdog.commands.core import parse_command_and_args
from feed_watchdog.rest_api.container import wire_modules

CURR_DIR = Path(__file__).parent


def main() -> None:
    setup()
    parser = argparse.ArgumentParser()
    worker, args = parse_command_and_args(
        parser=parser,
        path_to_commands=CURR_DIR / "commands",
        import_path="feed_watchdog.rest_api.commands",
    )
    worker.handle(args)


def setup() -> None:
    wire_modules()
    logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    main()
