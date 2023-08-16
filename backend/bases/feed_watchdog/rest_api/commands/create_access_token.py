import argparse
from argparse import ArgumentParser

from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.rest_api.auth import create_access_token


class CreateAccessTokenCommand(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--sub", required=True)
        parser.add_argument(
            "--expires_minutes", type=int, default=60 * 24 * 999
        )

    def handle(self, args: argparse.Namespace):
        print(
            create_access_token(
                subject=args.sub, expires_minutes=args.expires_minutes
            )
        )
