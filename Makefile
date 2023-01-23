SHELL:=/usr/bin/env bash

POETRY_RUN=poetry

.PHONY: lint
lint:
	$(POETRY_RUN) run flake8 server
	@make mypy
	@make verify_format
	$(POETRY_RUN) run doc8 -q docs
	$(POETRY_RUN) run yamllint -s .

.PHONY: mypy
mypy:
	$(POETRY_RUN) run mypy server/**/*.py

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
	$(POETRY_RUN) run black --preview server
	$(POETRY_RUN) run isort --color --src=server ./**/*.py server


.PHONY: verify_format
verify_format:
	$(POETRY_RUN) run black --preview --check --diff server
	$(POETRY_RUN) run isort --check-only --diff --src=server ./**/*.py server

.PHONY: bash
bash:
	docker compose exec feed_watchdog bash
