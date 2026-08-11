# AGENTS.md — env-alias

Entry point for AI agents working in this repository. Read this first, then the linked files.

## What this project is

`env-alias` is a CLI utility that reads a YAML *definitions file* and emits shell `export`
statements on **stdout**, intended to be consumed as:

```shell
alias "myenv"="source <(env-alias --generator ~/myenv.yml)"
```

Values are sourced from local files, HTTP URLs, shell commands, stdin/getpass prompts, KeePass
databases, and Ansible Vault files, then narrowed with a *parser* (`ini`/`json`/`yaml`/plaintext) and
a *selector* (dotted path or line number).

**The single most important invariant: stdout is shell code that the user's interactive shell will
execute.** Nothing may write to stdout except `EnvAliasGenerator.output_export()`. All logging,
prompts, and diagnostics go to stderr. Anything that lands on stdout unquoted is a code-execution
vector, not a formatting bug. (`value_to` targets stderr only — `<stdout>` was removed in 0.7.0.)

Secondary consequence: this tool handles plaintext secrets throughout. Treat every code path in
`lib/source.py` as security-sensitive.

## Required reading

| File | When |
|------|------|
| `rules/environment.md` | **Always.** Never create a local `.venv`. |
| `rules/dev-directory.md` | **Always.** `_dev/` is invisible — never read, write, or reference it. |
| `context/project_context.md` | Stack, architecture, and testing conventions. |
| `workflows/post-implementation-verification.md` | Before submitting any change. |
| `workflows/uv-commands.md` | If invoking `uv` directly rather than via `make`. |

The two `rules/` files are hard constraints, not suggestions. Violating them corrupts developer state.

## Commands

Use the `Makefile`. It already applies the `UV_PROJECT_ENVIRONMENT` / `UV_CACHE_DIR` /
`UV_LINK_MODE=copy` prefix required by `rules/environment.md`.

```shell
make setup        # create isolated venv + sync dev deps
make test         # pytest
make lint         # ruff check
make lint-fix     # ruff check --fix + ruff format
make typecheck    # basedpyright
make build        # wheel + sdist
make help         # full list
```

Never run bare `uv`, `pip`, `pytest`, or `ruff` — the isolation prefix is mandatory. If you need a
command the `Makefile` lacks, add a target rather than running it ad hoc.

## Layout

```
src/env_alias/
    __init__.py              # __version__ (single source of truth), LOGGER_*, DEFINITIONS_ROOT
    main.py                  # CLI entrypoint; two modes: alias emitter, and --generator
    exceptions.py            # EnvAliasException (logs itself on construction)
    lib/
        definitions.py       # YAML file -> list[EnvAliasDefinition]
        generator.py         # orchestrator; the only place that writes export lines
        source.py            # SOURCE_STRATEGIES: how to fetch raw content
        selector.py          # PARSER_STRATEGIES: how to narrow content to one value
        logger.py            # stderr logging, colourised level names
    models/
        envalias_definition.py   # pydantic v2 model of one YAML definition entry
        sourced_content.py       # pydantic v2 model of fetched content + metadata
tests/
    test_*.py                # pytest; most build a temp YAML file and assert on capsys
    manual/*.yml             # hand-run example definition files
docs/                        # mkdocs site, separate uv project with its own pyproject/lock
```

Control flow: `main.entrypoint` → `EnvAliasGenerator.generate()` → `EnvAliasDefinitions.load_definitions()`
→ per definition: `update_env_replacement_attributes` → `get_content_from_source` (source strategy) →
`get_definition_value` (parser strategy) → `output_export`.

## Domain concepts you must understand before editing

- **`SOURCE_STRATEGIES` / `PARSER_STRATEGIES`** (`lib/source.py`, `lib/selector.py`) — dispatch tables
  replacing former if/elif chains. `SOURCE_STRATEGIES` is an **ordered** list; the catch-all
  `bool(d.source)` predicate must remain after the more specific keepass/vault/stdin predicates.
  Order is load-bearing and currently unenforced by tests. Do not reorder casually.
- **`env:` indirection** — any definition attribute whose value starts with `env:` is replaced with
  the named environment variable, or with a value produced by an *earlier* definition in the same
  file (`generator.get_replacement_env_value`). This is how a password is fetched once and reused.
  It makes definition order significant.
- **`name: null`** — marks a definition as internal-only (`_is_internal_only`): the value is computed
  and made available to later definitions via `env:`, but is never exported. Used for intermediate
  secrets. A definition named the *string* `"none"`/`"None"` is a common user mistake and triggers a
  warning.
- **`selector: null` vs absent selector** — `definitions.py` maps YAML `null` to the string sentinel
  `"none"`, which suppresses output entirely; an absent selector means "default" (line 1 for
  plaintext). These are different behaviours encoded in a string value. `selector: none` spelled
  literally is legacy syntax and is pinned by a test.
- **`value_to: <stderr>`** — echoes the value to stderr (in addition to, or instead of when combined
  with `name: null`, exporting it). Only `<stderr>` is valid; `<stdout>` was removed in 0.7.0.
- **`override: false`** — skip the definition if the variable is already set.
- **`ansible_vault_password_file: true`** — special case that emits an *extra* export beyond the
  definition's own. `generator.source_map` maps the generated script path to the generated environment
  variable name, so the raw password is exported under that derived name for Ansible to read.

## Conventions

- Python `>=3.10` per `requires-python` — PEP 604 unions (`str | None`), not
  `typing.Optional`/`Union`. The migration to the new style is complete; match the new style.
- `pydantic` v2 for all models; `extra="forbid"` so unknown YAML keys are rejected loudly.
- Raise `EnvAliasException` for user-facing errors, with `detail=` for debug-only context. Always
  chain: `raise EnvAliasException(...) from e`.
- Line length 120, double quotes, ruff-formatted. Rules `E,W,F,I,B,C4,UP,SIM` (see `pyproject.toml`).
- Version lives only in `src/env_alias/__init__.py`; `pyproject.toml` reads it dynamically. Bump via
  `make bump-patch` / `make bump-minor` / `make bump-major`.
- Tests assert on the exact export format including its leading space
  (`' export "NAME"="value"'`) — the space suppresses shell history recording. Do not "clean it up".

## Current state (read before assuming anything)

The build/toolchain refactor is **complete and committed**: `hatchling` + `uv` + `Makefile`, models
on `pydantic` v2, strategy tables (`SOURCE_STRATEGIES`/`PARSER_STRATEGIES`) instead of if/elif
chains, typing on PEP 604. The deleted `pdm`/`slap`/`mypy`/`setuptools` toolchain is gone.

Consequences to be aware of:

- `.github/workflows/project-tests.yml` is the single CI test workflow; it runs `make lint`,
  `make typecheck`, and `make test-all` across Python 3.10–3.14. `.github/workflows/build-tests.yml`
  was deleted. `docs/docs/development.md` documents the current `uv`/`Makefile` workflow.
- `make lint`, `make typecheck`, and `make test` are quick checks. `make test-all` runs the full suite
  (including slow and network tests) and enforces the 80% coverage floor (`--cov-fail-under=80`) —
  use it before any release.
- `basedpyright` still has several `report* = "none"` overrides, so treat typecheck pass as a signal,
  not a guarantee of clean types.
- Version `0.7.1` lives only in `src/env_alias/__init__.py`, read dynamically by `pyproject.toml`; the
  release tag must match it (`v0.7.1`). The current working tree has an uncommitted documentation
  changeset (docs pages, workflows, badge examples) awaiting commit.
