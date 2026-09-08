VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
APP_HOST ?= 127.0.0.1
APP_PORT ?= 7860

.PHONY: bootstrap ontology-check secret-scan test live-llm-smoke e2e dev build run

bootstrap:
	test -x $(PYTHON) || python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"
	npm --prefix frontend ci

ontology-check:
	$(PYTHON) scripts/inspect_ontology.py --check

secret-scan:
	$(PYTHON) scripts/secret_scan.py

test: secret-scan
	$(PYTHON) -m pytest -m "not live"
	npm --prefix frontend run test

live-llm-smoke:
	@test "$${RUN_LIVE_LLM_TESTS:-0}" = "1" || (echo "Set RUN_LIVE_LLM_TESTS=1 to enable the synthetic live test." && exit 2)
	$(PYTHON) -m pytest -m live backend/tests/test_live_llm.py

e2e: build
	npm --prefix frontend run e2e

dev:
	./scripts/dev.sh

build:
	npm --prefix frontend run build

run: ontology-check build
	APP_HOST=$(APP_HOST) APP_PORT=$(APP_PORT) $(PYTHON) -m uvicorn app.main:app --app-dir backend --host $(APP_HOST) --port $(APP_PORT)
