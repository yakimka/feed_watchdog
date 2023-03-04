import os
import shutil


def collect_frontend() -> None:
    shutil.copytree("/app/frontend", "/var/www/frontend", dirs_exist_ok=True)
    envs = _get_app_envs()

    _prepare_html(envs)


def _get_app_envs() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        if key.startswith("VUE_APP_")
    }


def _prepare_html(data: dict) -> None:
    with open("/app/frontend/index.html", "r") as r, open(
        "/var/www/frontend/index.html", "w"
    ) as w:
        index = r.read()
        metas = []
        for key, value in data.items():
            index = index.replace(f"${key}", value)
            metas.append(f'<meta property="{key}" content="{value}">')

        metas_string = "".join(metas)
        head_index = index.index("<head>") + len("<head>")
        w.write(f"{index[:head_index]}{metas_string}{index[head_index:]}")


if __name__ == "__main__":
    collect_frontend()
    print("Done")
