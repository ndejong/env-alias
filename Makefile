# Makefile for env-alias
# Enforces isolated Python virtual environments using uv to prevent local .venv leakage.

.PHONY: help setup sync test test-verbose test-all coverage lint format lint-fix typecheck build smoke-wheel bump-patch bump-minor bump-major clean docs-sync docs-build docs-serve

.DEFAULT_GOAL := help

# UV execution prefix with environment isolation
UV := UV_PROJECT_ENVIRONMENT=$(HOME)/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv

# Show help menu of available commands
help:
	@echo "Available commands:"
	@echo "  make setup         - Create virtual environment and sync dependencies"
	@echo "  make sync          - Sync python dependencies (dev environment)"
	@echo "  make test          - Run fast offline unit and integration tests (skips network/slow)"
	@echo "  make test-verbose  - Run tests verbosely (skips network/slow)"
	@echo "  make test-all      - Run the full test suite incl. slow + network tests"
	@echo "  make lint          - Run linting checks (ruff)"
	@echo "  make format        - Format code (ruff)"
	@echo "  make lint-fix      - Auto-fix linting and formatting issues"
	@echo "  make typecheck     - Run type checking (basedpyright)"
	@echo "  make build         - Build wheel and source distributions"
	@echo "  make smoke-wheel   - Build wheel, install into throwaway venv, run CLI"
	@echo "  make bump-patch    - Bump the patch version number (e.g. 0.1.0 -> 0.1.1)"
	@echo "  make bump-minor    - Bump the minor version number (e.g. 0.1.0 -> 0.2.0)"
	@echo "  make bump-major    - Bump the major version number (e.g. 0.1.0 -> 1.0.0)"
	@echo "  make clean         - Clean build and cache artifacts"
	@echo "  make docs-sync     - Sync documentation dependencies"
	@echo "  make docs-build    - Build documentation with strict warning checks"
	@echo "  make docs-serve    - Serve documentation locally"

# Create virtual environment and sync dependencies
setup:
	@echo "Initializing isolated virtual environment..."
	$(UV) venv --clear $(HOME)/.local/venvs/env-alias
	@echo "Syncing dependencies..."
	$(UV) sync --extra dev

# Sync Python dependencies
sync:
	$(UV) sync --extra dev

# Run tests
test:
	$(UV) run --extra dev pytest

# Run tests verbosely
test-verbose:
	$(UV) run --extra dev pytest -v

# Run the full test suite including slow and network tests
test-all:
	$(UV) run --extra dev pytest -m "not network or network"

# Run tests with coverage
coverage:
	$(UV) run --extra dev pytest --cov=env_alias --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Run linting checks
lint:
	$(UV) run --extra dev ruff check src tests

# Format code
format:
	$(UV) run --extra dev ruff format src tests

# Auto-fix linting and formatting issues
lint-fix:
	$(UV) run --extra dev ruff check --fix src tests
	$(UV) run --extra dev ruff format src tests

# Run type checking
typecheck:
	$(UV) run --extra dev basedpyright

# Build distribution packages
build:
	$(UV) build

# Build the wheel, install it into a throwaway venv, and run the CLI.
# Regression guard: the setuptools migration once
# produced a wheel that dropped env_alias.lib / env_alias.models, which a
# --version-only smoke test would not have caught.
#
# `clean` removes stale wheels from a previous version, otherwise the
# dist/env_alias-*.whl install glob would pull conflicting URLs and the
# throwaway venv would never actually get the binary. The `&&` chain aborts on
# the first failing step instead of printing success through an error.
smoke-wheel: clean build
	@tmpdir=$$(mktemp -d); \
	trap 'rm -rf $$tmpdir' EXIT; \
	$(UV) venv $$tmpdir/venv \
	&& $(UV) pip install --python $$tmpdir/venv/bin/python dist/env_alias-*.whl \
	&& echo "-> wheel install OK" \
	&& $$tmpdir/venv/bin/env-alias --version \
	&& printf '\nenv-alias:\n  SMOKE:\n    source: %s/data.txt\n    selector: 1\n' "$$tmpdir" > $$tmpdir/def.yml \
	&& printf 'hello-wheel\n' > $$tmpdir/data.txt \
	&& $$tmpdir/venv/bin/env-alias --generator $$tmpdir/def.yml \
	&& echo "-> generator run OK"

# Clean build/test/cache artifacts
clean:
	rm -rf dist build *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# Bump the patch version number (e.g. 0.1.0 -> 0.1.1)
bump-patch:
	$(UV) run --extra dev hatch version patch

# Bump the minor version number (e.g. 0.1.0 -> 0.2.0)
bump-minor:
	$(UV) run --extra dev hatch version minor

# Bump the major version number (e.g. 0.1.0 -> 1.0.0)
bump-major:
	$(UV) run --extra dev hatch version major

# UV configuration for documentation (isolated to prevent package dev conflict)
DOCS_UV = UV_PROJECT_ENVIRONMENT=$(HOME)/.local/venvs/env-alias-docs UV_CACHE_DIR=/tmp/.uv-cache-env-alias-docs UV_LINK_MODE=copy uv

# Sync documentation dependencies
docs-sync:
	cd docs && $(DOCS_UV) sync

# Build documentation site
docs-build:
	cd docs && $(DOCS_UV) run mkdocs build --strict

# Serve documentation locally
docs-serve:
	cd docs && $(DOCS_UV) run mkdocs serve
