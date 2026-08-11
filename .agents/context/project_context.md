# Project Context: env-alias

Welcome to the `env-alias` codebase context. This document outlines the core stack, architecture, design decisions, and coding standards.

Read `../AGENTS.md` first for the repository map, control flow, domain concepts, and current
working-tree state. This file covers the stack, the *why* behind the design, and testing conventions.

---

## 🛠 Core Stack

| Concern | Choice | Notes |
|---------|--------|-------|
| Language | Python `>=3.10` | PEP 604 unions available. |
| Runtime deps | `pyyaml`, `pydantic>=2` | Deliberately minimal — this is a shell-startup-path tool, so import time matters. `requests` is a **dev/test** dep only; runtime HTTP uses stdlib `urllib.request`. |
| Build backend | `hatchling` | `src/` layout (`[tool.hatch.build.targets.wheel] packages = ["src/env_alias"]`); version kept in `env_alias.__version__` and read dynamically via `[tool.hatch.version] path`. Publish install uses `uv`/PyPI, not `setuptools`. |
| Env / deps | `uv` | Isolated environment, never a repo-local `.venv`. See `../rules/environment.md`. |
| Task runner | `make` | `Makefile` wraps every `uv` invocation with the required isolation prefix. |
| Lint + format | `ruff` 0.16 | Rules `E,W,F,I,B,C4,UP,SIM`; line length 120; double quotes. |
| Type checker | `basedpyright` 1.39.9 | `typeCheckingMode = "standard"`, `pythonVersion = "3.10"`; 7 `report* = "none"` overrides and 5 `report* = "warning"` (see `pyproject.toml`) — pass is a signal, not a guarantee. |
| Tests | `pytest` | `pytest-cov` with `--cov-fail-under=80`; markers `network`, `slow`, `requires_keepassxc`, `requires_ansible_vault`. Coverage is measured. |
| Docs | `mkdocs-material` | `docs/` is a **separate uv project** with its own `pyproject.toml` and `uv.lock`, pinned to Python 3.12. Use the `docs-*` Makefile targets (`docs-build` runs `mkdocs build --strict`). |
| CLI surface | stdlib only | Argument parsing is hand-rolled in `main.py`, not `argparse`. |

Historical note: the project previously used `pdm` + `slap-cli` + `mypy`. Those are gone from
`pyproject.toml` and their old workflow files (`build-tests.yml`) were deleted. Ignore them as
guidance; they describe a toolchain that no longer exists. `asciidoctor`/`slap` references elsewhere
are likewise defunct.

---

## 🏗 Architecture & Design Decisions

### The stdout contract

`env-alias` output is `source`d directly by the user's interactive shell:

```shell
alias "myenv"="source <(env-alias --generator ~/myenv.yml)"
```

Everything else follows from this:

* **stdout is executable shell code.** Only `EnvAliasGenerator.output_export()` may write to it.
  Logging, prompts, and errors go to stderr (`lib/logger.py` uses `StreamHandler()`, which defaults to
  stderr). `value_to` targets stderr only — `<stdout>` was removed in 0.7.0.
* **Values must be shell-escaped, not merely quoted.** They routinely contain `"`, `$`, and backticks
  because they are passwords. Unescaped interpolation is a code-execution defect, not a cosmetic one.
* **Exported lines are prefixed with a single space** so the shell omits them from history when
  `HISTCONTROL=ignorespace`. Roughly fifteen tests assert this prefix. It is intentional.
* **Exit status is a correctness signal.** A non-zero status is the only way the caller learns that
  the sourced output is incomplete.

### Layered pipeline

```
main.py            argument handling, alias-string emission
  └─ generator.py  orchestration, env-var bookkeeping, output
       ├─ definitions.py  YAML  -> list[EnvAliasDefinition]
       ├─ source.py       where  -> SourcedContent   (SOURCE_STRATEGIES)
       └─ selector.py     which  -> str             (PARSER_STRATEGIES)
```

The split is *acquisition* (`source.py`: how bytes are obtained) versus *narrowing*
(`selector.py`: which value inside those bytes is wanted). `SourcedContent` is the seam between them
and carries a `content_type` sniffed from the source, which a definition's explicit `parser` may
override. `generator.py` is the only module aware of both halves, and the only module that mutates
process state.

### Strategy tables over conditional chains

`SOURCE_STRATEGIES` (`lib/source.py`) and `PARSER_STRATEGIES` (`lib/selector.py`) replaced long
`if/elif` chains. Rationale: adding a source or parser becomes a table entry rather than an edit to a
branch chain, and each entry is independently testable.

Trade-off accepted, and worth knowing: `SOURCE_STRATEGIES` is an **ordered list of predicates**, and
first-match-wins. The catch-all `bool(d.source)` local-file entry must remain last among the
`source`-based predicates, and `bool(d.exec)` after it. This ordering is load-bearing and not yet
enforced by any test.

### Models as the validation boundary

`pydantic` v2 models (`models/`) are where malformed definitions are rejected:

* `extra="forbid"` — a typo'd YAML key is an error, not a silently ignored field. For a secrets tool,
  silently ignoring `overide: false` would be dangerous.
* Field validators normalise input (`selector` coerced to `str`, `parser`/`value_to` lowercased,
  YAML-ish booleans `yes`/`no` accepted).
* `check_cross_field_constraints` (a `model_validator`) enforces mutual exclusivity —
  `exec` xor `source` xor `value`, `keepass_password` xor `ansible_vault_password`, and the
  `ansible_vault_password_file` pairing rules.

Consequence: **validation belongs in the model, not in `generator.py`.** When adding an attribute,
add its constraints as validators so failures surface at load time, before any secret is fetched or
any command is run.

`name` is a non-optional `str`; `filename` and `is_internal_only` are real model fields
(`filename` is `exclude=True` and is set from the source file path by `definitions.py`), so a
constructed instance is complete. Validation rejects conflicting combinations up front (e.g.
`exec` xor `source` xor `value`).

### Sequential, order-dependent evaluation

Definitions are processed in file order, and each one can consume earlier results:

* `env:<NAME>` in any attribute resolves against `os.environ` first, then against
  `values_generated` (values produced earlier in this run). This is how a KeePass password is
  prompted once and reused by several entries.
* Resolved values are written into `os.environ` so that later `exec:` subprocesses inherit them.

So the generator is a small interpreter with mutable state, not a pure map over definitions. Two
implications: reordering definitions changes behaviour, and tests must isolate `os.environ`.

### Secret handling posture

The tool's entire purpose is moving plaintext secrets, so:

* Secrets pass through `os.environ`, subprocess pipes, and (for Ansible Vault) a temporary file.
* Prefer stdin over command lines and environment variables for handing secrets to child processes.
* `shell=True` is *intentional and documented* for the user-facing `exec:` attribute
  (`docs/docs/security.md`, `docs/docs/definition-attributes/exec.md`). It is **not** acceptable for
  built-in integrations, where arguments derive from selectors and file paths — use argv lists there.
* Debug logging currently emits secret values and command lines verbatim. Assume `--debug` output is
  sensitive.

### Escape hatches, deliberately

`<stdin>`, `<getpass>`, `<stderr>`, `name: null`, and `selector: null` are sentinel values
in the YAML surface. They exist so the definition file stays a flat dict of simple scalars — no nested
config schema. The cost is control flow keyed on magic strings scattered across modules; these are
backed by typed constants (`SourceMethod`, `ParserType`, `SelectorType`, `ValueTo`) while the YAML
spellings remain public API and must keep working.

---

## 🧪 Testing Guidelines

Prefer the Makefile targets — they already apply the isolation prefix:

```bash
make test           # pytest
make test-verbose   # pytest -v
```

If invoking `uv` directly, always run the tests using isolated virtual environment prefixes to prevent
`.venv` directory creation in the repository:

```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias \
UV_CACHE_DIR=/tmp/.uv-cache-env-alias \
UV_LINK_MODE=copy \
uv run --extra dev pytest
```

### How the tests are written

Most tests follow one shape: build a YAML definitions file in a temp location, run
`EnvAliasGenerator(config_file=...).generate()`, and assert against `capsys`. The `config_file`
fixture in `tests/conftest.py` writes the given YAML (prepending the `env-alias:` root) to a temp path:

```python
def test_something(capsys, config_file):
    yaml = """
    MY_VAR:
        value: 'hello'
    """
    EnvAliasGenerator(config_file=config_file(yaml)).generate()

    captured = capsys.readouterr().out.rstrip()
    assert ' export "MY_VAR"="hello"' in captured
```

Note the leading space in the assertion — see the stdout contract above.

`tests/manual/*.yml` are hand-run example definition files, not pytest fixtures. Use them for the
manual verification step in `../workflows/post-implementation-verification.md`.

### Conventions and current shortcomings

* Assert on **stdout vs stderr separately**. `capsys.readouterr()` drains both, so a second call
  returns empty — several existing tests rely on this ordering.
* Tests mutate global `os.environ` (the generator does so by design). There is an autouse
  `isolate_environ` fixture in `tests/conftest.py` that snapshots and restores it; rely on that rather
  than restoring manually.
* `tests/conftest.py` provides reusable fixtures (`config_file`, `mkdocs_nav`, `isolate_environ`).
  Prefer them over copy-pasting the old `__generate_config_file` helper into new test modules.
* `tests/__init__.py` contains an unused helper and a stale `sys.path.append` pointing at a
  pre-`src/`-layout directory. Do not extend it.
* Network tests are marked `network`, and KeePass/Ansible-Vault tests require their binaries. The
  default `make test` run excludes `network` and `slow` markers; binary-requiring tests `skipif` the
  binary is absent. When adding such a test, gate it with the appropriate marker plus
  `shutil.which(...)` / `skipif` rather than assuming the dependency exists.

### What to test when touching security-sensitive paths

Any change to output formatting, `lib/source.py`, or selector resolution should come with tests that
round-trip through a real shell (`bash -c 'source ...'`) and assert byte-identical values for inputs
containing `"`, `'`, `` ` ``, `$`, `$(...)`, `\`, `;`, newlines, and leading/trailing whitespace.
Assertions on the generated *string* alone will not catch shell-evaluation defects.
