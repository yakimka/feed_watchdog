SHELL:=/usr/bin/env bash

ENTRYPOINT=docker compose run --rm -it feed_watchdog
POETRY_RUN=$(ENTRYPOINT) poetry
SRC_DIR=.


.PHONY: lint
lint:
	@make flake8
	@make mypy
	@make verify_format
	$(POETRY_RUN) run doc8 -q docs
	#$(POETRY_RUN) run yamllint -s .

.PHONY: flake8
flake8:
	$(POETRY_RUN) run flake8 $(SRC_DIR)

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

.PHONY: safety
safety:
	$(POETRY_RUN) run safety check --full-report

.PHONY: test
test: lint package unit

.PHONY: format
format:
	$(POETRY_RUN) run black --preview $(SRC_DIR)
	$(POETRY_RUN) run isort --color --src=$(SRC_DIR) $(SRC_DIR)


.PHONY: verify_format
verify_format:
	$(POETRY_RUN) run black --preview --check --diff $(SRC_DIR)
	$(POETRY_RUN) run isort --check-only --diff --src=$(SRC_DIR) $(SRC_DIR)

.PHONY: run_command
run_command:
	$(POETRY_RUN) run python -m feed_watchdog.rest_api.cli.$(args)

.PHONY: bash
bash:
	$(ENTRYPOINT) bash

.PHONY: poetry
poetry:
	$(POETRY_RUN) $(args)
