# Usage

## Build the project
Navigate to this folder (where the `pyproject.toml` file is)

Run:
``` shell
poetry build-project
```

## Build a docker image

``` shell
docker build -t feed_watchdog .
```

## Run the image

``` shell
docker run --rm --name feed_watchdog -p 8000:8000 feed_watchdog
```

The OpenAPI specification of this FastAPI app can now be accessed at http://localhost:8000/docs/

