ARG FRONTEND_IMAGE=feed_watchdog_frontend:latest
FROM $FRONTEND_IMAGE as frontend


FROM python:3.11-slim-bullseye as builder

ARG WHEEL=feed_watchdog_api-0.1.0-py3-none-any.whl
ENV VIRTUAL_ENV=/venv

WORKDIR /code

RUN python -m venv $VIRTUAL_ENV

# for caching purposes in CI
# waiting for https://github.com/moby/buildkit/issues/1512
# to replace with this:
#COPY ./dist/$WHEEL ./$WHEEL
#RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
#    pip install --upgrade pip \
#    && pip install --upgrade wheel \
#    && pip install --upgrade ./$WHEEL
COPY ./dist/requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip \
    && pip install --upgrade --no-cache-dir wheel \
    && pip install --upgrade --no-cache-dir -r requirements.txt

COPY ./dist/$WHEEL ./$WHEEL
RUN pip install --upgrade --no-cache-dir ./$WHEEL --no-deps


FROM python:3.11-slim-bullseye as production
COPY --from=frontend /app/frontend/dist /frontend

RUN useradd -M appuser --uid=1000 --shell=/bin/false
USER appuser
ENV VIRTUAL_ENV=/venv

WORKDIR /opt/app

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

CMD ["uvicorn", "feed_watchdog.rest_api.core:app", "--host", "0.0.0.0", "--port", "8000"]
