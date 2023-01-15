# https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# `python-base` sets up all our shared environment variables
FROM python:3.10-slim-bullseye as python-base

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
    POETRY_VERSION=1.1.13 \
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
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    XDG_CACHE_HOME="/app/.cache"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN addgroup --gid 1000 --system app \
    && adduser --uid 1000 --system --no-create-home --shell=/bin/false --disabled-password --group app \
    && mkdir /app \
    && chown -R 1000:1000 /app

RUN apt-get update && \
apt-get install --no-install-recommends -y  \
    make \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


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

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

RUN mkdir -p /var/www/public/{media,static} \
    && chown -R 1000:1000 /var/www/public


# `development` image is used during development / testing
FROM python-base as development
ENV ENVIRONMENT=development \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

# will become mountpoint of our code
WORKDIR /app/server

# for installing deps without rebuild image
ENV PATH="/app/.venv/bin:$PATH"

USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]


# `production` image used for runtime
FROM python-base as production
ENV ENVIRONMENT=production \
    WEB_CONCURRENCY=4
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --chown=app:app server /app/server
WORKDIR /app/server

USER app

CMD ["gunicorn", "wsgi", "-b", "0.0.0.0:8000", "--timeout=90", "--log-file=-"]
