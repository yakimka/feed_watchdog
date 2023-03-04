import argparse

from auth import create_access_token
from commands.core import BaseCommand


class CreateAccessTokenCommand(BaseCommand):
    def run(self, args: argparse.Namespace):
        print(
            create_access_token(
                subject=args.sub, expires_minutes=args.expires_minutes
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub", required=True)
    parser.add_argument("--expires_minutes", type=int, default=30)

    CreateAccessTokenCommand().run(parser.parse_args())
