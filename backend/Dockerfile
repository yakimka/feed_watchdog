# https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# `python-base` sets up all our shared environment variables
FROM python:3.11-slim as python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.5.1 \
    # make poetry install to this location
    VENV_PATH="/opt/venv" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    APP_PATH="/app" \
    XDG_CACHE_HOME="/app/.cache" \
    XDG_CONFIG_HOME="/app/.cache/config"

# prepend poetry and venv to path
ENV PATH="$VENV_PATH/bin:$APP_PATH/.venv/bin:$PATH"
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER_NAME=app

RUN addgroup --gid $GROUP_ID --system $USER_NAME \
    && adduser --uid $USER_ID --system --no-create-home --shell=/bin/false --disabled-password --group $USER_NAME \
    && mkdir /app \
    && chown -R $USER_ID:$GROUP_ID /app

RUN apt-get update && \
apt-get install --no-install-recommends -y  \
    make \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/frontend \
    && chown -R $USER_ID:$GROUP_ID /var/www/frontend

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base
RUN set -ex \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        libpq-dev

RUN python -m venv /opt/venv
RUN pip install poetry==$POETRY_VERSION \
    && poetry self add poetry-multiproject-plugin poetry-polylith-plugin


# `development` image is used during development / testing
FROM python-base as development
ARG USER_NAME=app
ENV ENVIRONMENT=development \
    PYTHONDONTWRITEBYTECODE=1

RUN set -ex \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    # for pre-commit
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $VENV_PATH $VENV_PATH

USER $USER_NAME

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "feed_watchdog.rest_api.core:app", "--host=0.0.0.0", "--port=8000", "--reload"]
