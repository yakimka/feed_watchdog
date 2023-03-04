SHELL:=/usr/bin/env bash

DOCKER_VERSION := $(shell docker --version 2>/dev/null)
ifdef DOCKER_VERSION
    POETRY_RUN=docker compose run --workdir=/app --rm devtools poetry
else
    POETRY_RUN=poetry
endif
SRC_DIR=server


.PHONY: lint
lint:
	$(POETRY_RUN) run flake8 $(SRC_DIR)
	@make mypy
	@make verify_format
	$(POETRY_RUN) run doc8 -q docs
	#$(POETRY_RUN) run yamllint -s .

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

.PHONY: collectstatic
collectstatic:
	$(POETRY_RUN) run python -m  server.commands.collectstatic

.PHONY: bash
bash:
	docker compose run --rm devtools bash

.PHONY: poetry
poetry:
	$(POETRY_RUN) $(args)
