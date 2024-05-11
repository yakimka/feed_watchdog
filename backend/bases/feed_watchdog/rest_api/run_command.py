import argparse
import logging
from pathlib import Path

import picodi

from feed_watchdog.commands.core import choose_and_setup_command, find_commands_in_dir

CURR_DIR = Path(__file__).parent


def main() -> None:
    setup()
    commands = list(
        find_commands_in_dir(CURR_DIR / "commands", "feed_watchdog.rest_api.commands")
    )
    picodi.init_resources()
    parser = argparse.ArgumentParser()
    worker, args = choose_and_setup_command(
        parser=parser,
        commands_to_setup=commands,
    )
    worker.handle(args)


def setup() -> None:
    logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    main()
