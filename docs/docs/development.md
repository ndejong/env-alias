# Development

Env Alias uses **uv** (with a project-specific Python environment) plus **Makefile** targets that wrap every
Python invocation. This keeps the toolchain isolated and prevents a local `.venv/` from being accidentally created
in the project tree.

## Prerequisites

* Python 3.10+ and [uv](https://docs.astral.sh/uv/) installed.
* `keepassxc-cli` and `ansible-vault` on `PATH` when exercising their integration tests.

## Environment isolation

All `make` targets route Python through uv with:

```make
UV := UV_PROJECT_ENVIRONMENT=$(HOME)/.local/venvs/env-alias UV_CACHE_DIR=/tmp/.uv-cache-env-alias UV_LINK_MODE=copy uv
```

This pins the venv to a stable path outside the project (so no `.venv/` appears in the working tree) and uses a
shared cache. **Do not run bare `uv run`, `pip`, or `pytest`** — use the Makefile targets.

## Set up the development environment

```shell
make setup      # create the isolated venv and sync dev dependencies
make sync       # re-sync dependencies after a change to pyproject.toml / uv.lock
```

## Common tasks

```shell
make lint         # ruff lint check (src + tests)
make format       # ruff format (src + tests)
make lint-fix     # ruff check --fix + format, apply fixes
make typecheck    # basedpyright static type checking (src + tests)
make test         # run the fast offline unit and integration tests (skips network/slow)
make test-verbose # run tests verbosely
make test-all     # run the full suite incl. slow + network tests
make coverage     # run tests with a coverage report (html + terminal)
make build        # build sdist + wheel into dist/
make smoke-wheel  # build the wheel, install into a throwaway venv, run the CLI
make docs-sync    # sync the separate documentation environment
make docs-build   # build documentation with strict warning checks
make docs-serve   # serve documentation locally
```

## Code quality gates

Before committing, run the non-mutating checks:

```shell
make lint && make typecheck && make test
```

`make lint-fix` changes files, so use it only when you intend to apply Ruff fixes and formatting.
`make test` excludes tests marked `network` or `slow`. Before a release, also run:

```shell
make test-all && make build && make smoke-wheel
```

## Writing a test first

For defect fixes the convention is to **write a failing test first**, watch it fail, then
fix the code so it passes. Tests live in `tests/`, use the shared `config_file` and `isolate_environ` fixtures from
`tests/conftest.py`, and are run through `make test`.

## Version bumping and release

The version is single-sourced from `src/env_alias/__init__.py` (`__version__`), picked up dynamically by
`pyproject.toml` via `[tool.hatch.version] path`. To cut a release:

1. Run the release checks above.
2. Bump `__version__` in `src/env_alias/__init__.py` with `make bump-major` / `make bump-minor` /
   `make bump-patch` (wraps `hatch version`).
3. Commit, then push a `vX.Y.Z` tag. The tag-triggered PyPI workflow verifies that the tag matches
   `__version__`, builds the distributions, creates a GitHub release, and publishes to PyPI via trusted
   publishing. It does not rerun the quality gates, so run them before tagging.

## Where things live

* `src/env_alias/main.py` — CLI entry point and alias-mode output.
* `src/env_alias/lib/generator.py` — core generation loop, export output (batching, quoting, redaction).
* `src/env_alias/lib/definitions.py` — YAML loading and validation into `EnvAliasDefinition` models.
* `src/env_alias/lib/source.py` — the data-source strategies (local, remote, exec, stdin, getpass, keepass, ansible-vault).
* `src/env_alias/lib/selector.py` — JSON/YAML paths, INI section/option selectors, and plaintext line selection.
* `src/env_alias/models/` — pydantic models and typed constants.
