SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run flake8 server
	poetry run mypy server/**/*.py
	make verify_format
	poetry run doc8 -q docs
	poetry run yamllint -s .

.PHONY: unit
unit:
	poetry run pytest

.PHONY: package
package:
	poetry check
	#poetry run pip check
	poetry run safety check --full-report

.PHONY: test
test: lint package unit

.PHONY: format
format:
	poetry run black --preview server
	poetry run isort --color --src=server ./**/*.py server


.PHONY: verify_format
verify_format:
	poetry run black --preview --check --diff server
	poetry run isort --check-only --diff --src=server ./**/*.py server
