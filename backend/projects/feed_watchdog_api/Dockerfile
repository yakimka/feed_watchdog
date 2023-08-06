FROM python:3.11-slim

ARG wheel=feed_watchdog_api-0.1.0-py3-none-any.whl

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$wheel /code/$wheel
RUN pip install --no-cache-dir --upgrade /code/$wheel

CMD ["uvicorn", "feed_watchdog.rest_api.core:app", "--host", "0.0.0.0", "--port", "8000"]
