# https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# `python-base` sets up all our shared environment variables
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDEVMODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.5.1 \
    VENV_PATH="/opt/venv" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    CODE_PATH="/opt/code" \
    BACKEND_PATH="/opt/code/backend"

ENV XDG_CACHE_HOME="$CODE_PATH/.cache" \
    XDG_CONFIG_HOME="/tmp/.config"


ENV PATH="$VENV_PATH/bin:$BACKEND_PATH/.venv/bin:$PATH"
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER_NAME=app

RUN addgroup --gid $GROUP_ID --system $USER_NAME \
    && adduser --uid $USER_ID --system --no-create-home --shell=/bin/false --disabled-password --group $USER_NAME \
    && mkdir $CODE_PATH \
    && chown -R $USER_ID:$GROUP_ID $CODE_PATH

RUN apt-get update \
  && apt-get install --no-install-recommends -y  \
    make \
    git \
    libpq5 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/frontend \
    && chown -R $USER_ID:$GROUP_ID /var/www/frontend

# For pre-commit
RUN mkdir -p $XDG_CONFIG_HOME/git \
    && touch $XDG_CONFIG_HOME/git/config \
    && chown -R $USER_ID:$GROUP_ID $XDG_CONFIG_HOME \
    && git config --global safe.directory $CODE_PATH


FROM python-base as builder-base
RUN set -ex \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for building python deps
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv $VENV_PATH
RUN pip install poetry==$POETRY_VERSION \
    && poetry self add poetry-multiproject-plugin poetry-polylith-plugin


# `development` image is used during development / testing
FROM python-base as development
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR $BACKEND_PATH

COPY --from=builder-base $VENV_PATH $VENV_PATH

USER $USER_NAME

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "feed_watchdog.rest_api.core:app", "--host=0.0.0.0", "--port=8000", "--reload"]
