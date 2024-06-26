import importlib
from argparse import ArgumentParser, Namespace
from inspect import isclass
from pathlib import Path
from typing import Awaitable, Generator


class BaseCommand:
    def setup(self) -> None:
        pass

    def handle(self, args: Namespace) -> Awaitable | None:
        raise NotImplementedError

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass


CURR_DIR = Path(__file__).parent


def find_commands_in_dir(
    path_to_commands: Path, import_path: str
) -> Generator[tuple[str, type[BaseCommand]], None, None]:
    for file in path_to_commands.glob("*.py"):
        module_name = file.stem
        if module_name == "__init__":
            continue
        module = importlib.import_module(f"{import_path}.{module_name}")
        for command_cls in module.__dict__.values():
            if (
                command_cls is not BaseCommand
                and isclass(command_cls)
                and issubclass(command_cls, BaseCommand)
            ):
                yield module_name, command_cls
                break


def choose_and_setup_command(
    parser: ArgumentParser,
    commands_to_setup: list[tuple[str, type[BaseCommand]]],
    dest="command",
) -> tuple[BaseCommand, Namespace]:
    subparsers = parser.add_subparsers(dest=dest, required=True)

    commands = {}
    for module_name, command_cls in commands_to_setup:
        command = command_cls()
        sub_parser = subparsers.add_parser(module_name)
        command.add_arguments(sub_parser)
        commands[module_name] = command

    args = parser.parse_args()
    command = commands[getattr(args, dest)]
    command.setup()
    return command, args
