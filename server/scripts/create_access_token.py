import argparse

from auth import create_access_token

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub", required=True)
    parser.add_argument("--expires_minutes", type=int, default=30)
    args = parser.parse_args()

    print(
        create_access_token(
            subject=args.sub, expires_minutes=args.expires_minutes
        )
    )
