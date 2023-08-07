import os
import shutil

from feed_watchdog.commands.core import BaseCommand

FRONTEND_SOURCE_DIR = "/app/frontend"
FRONTEND_DEST_DIR = "/var/www/frontend"


class CollectStatic(BaseCommand):
    def handle(self, args) -> None:  # noqa: U100
        shutil.copytree(
            FRONTEND_SOURCE_DIR, FRONTEND_DEST_DIR, dirs_exist_ok=True
        )
        envs = _get_app_envs()

        _prepare_html(envs)
        print("Done")


def _get_app_envs() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        if key.startswith("VUE_APP_")
    }


def _prepare_html(data: dict) -> None:
    with open(f"{FRONTEND_SOURCE_DIR}/index.html", "r") as r, open(
        f"{FRONTEND_DEST_DIR}/index.html", "w"
    ) as w:
        index = r.read()
        metas = []
        for key, value in data.items():
            index = index.replace(f"${key}", value)
            metas.append(f'<meta property="{key}" content="{value}">')

        metas_string = "".join(metas)
        head_index = index.index("<head>") + len("<head>")
        w.write(f"{index[:head_index]}{metas_string}{index[head_index:]}")
