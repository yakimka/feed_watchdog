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
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    APP_PATH="/app" \
    XDG_CACHE_HOME="/app/.cache"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$APP_PATH/.venv/bin:$PATH"

RUN addgroup --gid 1000 --system app \
    && adduser --uid 1000 --system --no-create-home --shell=/bin/false --disabled-password --group app \
    && mkdir /app \
    && chown -R 1000:1000 /app

RUN apt-get update && \
apt-get install --no-install-recommends -y  \
    make \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/frontend \
    && chown -R 1000:1000 /var/www/frontend

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

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python
RUN poetry self add poetry-multiproject-plugin poetry-polylith-plugin

# copy project requirement files here to ensure they will be cached.
WORKDIR $APP_PATH


# `development` image is used during development / testing
FROM python-base as development
ENV ENVIRONMENT=development \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR $APP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $APP_PATH $APP_PATH

USER app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "feed_watchdog.rest_api.core:app", "--host=0.0.0.0", "--port=8000", "--reload"]
