.PHONY: help install dev-install test lint format clean run reindex verify

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in editable mode
	pip install -e .

dev-install:  ## Install with dev dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	pytest tests/ -v --cov=mini_datahub --cov-report=html --cov-report=term

lint:  ## Run linters (ruff + mypy)
	ruff check mini_datahub tests
	mypy mini_datahub || true

format:  ## Format code with black
	black mini_datahub tests

format-check:  ## Check code formatting without modifying
	black --check mini_datahub tests

clean:  ## Clean up generated files
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-db:  ## Remove database (will be recreated on next run)
	rm -f db.sqlite db.sqlite-journal

run:  ## Launch the TUI
	hei-datahub

reindex:  ## Rebuild search index from YAML files
	hei-datahub reindex

verify:  ## Verify installation
	./scripts/verify_installation.sh

setup:  ## Run automated setup script
	./scripts/setup_dev.sh

check-all: format-check lint test  ## Run all checks (format, lint, test)

docs-serve:  ## Serve user documentation locally (http://localhost:8000)
	mkdocs serve

docs-dev-serve:  ## Serve developer documentation locally (http://localhost:8001)
	mkdocs serve -f mkdocs-dev.yml -a localhost:8001

docs-tutorial-serve:  ## Serve tutorial documentation locally (http://localhost:8002)
	mkdocs serve -f mkdocs-tutorial.yml -a localhost:8002

docs-serve-all:  ## Serve all documentation (requires 3 terminals or tmux)
	@echo "Run these in separate terminals:"
	@echo "  make docs-serve          # User docs on :8000"
	@echo "  make docs-dev-serve      # Dev docs on :8001"
	@echo "  make docs-tutorial-serve # Tutorial docs on :8002"

.DEFAULT_GOAL := help
