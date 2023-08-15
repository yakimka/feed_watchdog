FROM python:3.11-slim
COPY --from=feed_watchdog_frontend:latest /app/frontend/dist /app/frontend

ARG WHEEL=feed_watchdog_api-0.1.0-py3-none-any.whl

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$WHEEL /code/$WHEEL
RUN pip install --no-cache-dir --upgrade /code/$WHEEL

CMD ["uvicorn", "feed_watchdog.rest_api.core:app", "--host", "0.0.0.0", "--port", "8000"]
