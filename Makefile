#!/usr/bin/make -f
# Convenience targets for development

PY := python
PIP := $(PY) -m pip

.PHONY: setup dev format lint clean run-server run-client

setup:
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	@if [ -f dev-requirements.txt ]; then $(PIP) install -r dev-requirements.txt; fi

# Install dev-only tools
dev:
	$(PIP) install -r dev-requirements.txt

format:
	black .
	ruff check . --fix

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache ruff_cache .ruff_cache

run-server:
	$(PY) run_server.py

run-client:
	$(PY) client.py
