#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# Initializing global variables and functions:
: "${CI:=0}"
: "${DOCKER_XDG_CONFIG_HOME:=/app/.cache/config}"


pyclean () {
  echo 'cleaning up...'
  docker stop local-ci || true
}

run_ci () {
  echo '[ci started]'
  set -x  # we want to print commands during the CI process.

  # Run checks
  echo 'Run container with code and dev dependencies...'
  docker run \
    -di \
    --rm \
    --name=local-ci \
    -u $(id -u):$(id -g) \
    -v $(pwd)/..:/app \
    --workdir=/app/backend \
    feed_watchdog:dev \
    sleep infinity \
    || true
  EXEC="docker exec -i local-ci "
  $EXEC mkdir -p $DOCKER_XDG_CONFIG_HOME/git
  $EXEC touch $DOCKER_XDG_CONFIG_HOME/git/config
  $EXEC git config --global safe.directory /app

  $EXEC poetry install
  $EXEC git --version
  $EXEC poetry run pre-commit run --all-files
  $EXEC poetry run mypy
  $EXEC poetry run pytest
  # try to build package
  $EXEC bash -c "cd projects/feed_watchdog_api && poetry build-project"

  set +x
  echo '[ci finished]'
}

# Remove any cache before the script:
pyclean

# Clean everything up:
trap pyclean EXIT INT TERM

# Run the CI process:
run_ci
