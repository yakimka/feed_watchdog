SHELL:=/usr/bin/env bash

ENTRYPOINT=docker compose run --rm -it feed_watchdog_api
POETRY_RUN=$(ENTRYPOINT) poetry
SRC_DIR=.


.PHONY: mypy
mypy:
	$(POETRY_RUN) run mypy $(SRC_DIR)

.PHONY: unit
unit:
	$(POETRY_RUN) run pytest

.PHONY: package
package:
	$(POETRY_RUN) check
	#$(POETRY_RUN) run pip check

.PHONY: test
test: lint package unit

.PHONY: run_command
run_command:
	$(POETRY_RUN) run python -m feed_watchdog.rest_api.cli.$(args)

.PHONY: bash
bash:
	$(ENTRYPOINT) bash

.PHONY: poetry
poetry:
	$(POETRY_RUN) $(args)
