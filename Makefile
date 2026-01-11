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
	pytest tests/ -v --cov=hei_datahub --cov-report=html --cov-report=term

lint:  ## Run linters (ruff + mypy)
	ruff check hei_datahub tests
	mypy hei_datahub || true

format:  ## Format code with black
	black hei_datahub tests

format-check:  ## Check code formatting without modifying
	black --check hei_datahub tests

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

build-windows:  ## Build Windows exe and installer (run from WSL, requires PowerShell)
	@echo "Building Windows executable and installer..."
	powershell.exe -ExecutionPolicy Bypass -File ./scripts/build_windows.ps1

build-linux:  ## Build Linux binary
	./scripts/build_desktop_binary.sh

generate-icon:  ## Generate Windows icon from SVG
	python scripts/generate_icon.py

.DEFAULT_GOAL := help
