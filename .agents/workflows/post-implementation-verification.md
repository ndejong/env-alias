# Post-Implementation Verification Checklist

Before submitting any code changes, complete the following verification steps. Use the `Makefile`
targets — they already apply the required `UV_PROJECT_ENVIRONMENT` / `UV_CACHE_DIR` /
`UV_LINK_MODE=copy` isolation prefix.

---

## 1. Code Formatting & Linting

```bash
make lint
```

Auto-fix linting and formatting issues:

```bash
make lint-fix
```

---

## 2. Type Checking

```bash
make typecheck
```

---

## 3. Automated Testing

Run the full suite (includes slow and network tests and enforces the 80% coverage floor):

```bash
make test-all
```

---

## 4. Manual Verification

Verify the CLI works as expected by running it with a sample configuration file:

1. Run the generator with a sample configuration:
   ```bash
   make test-all   # quick unit pass is sufficient here unless behaviour changed
   ```
   or run the generator directly on a manual fixture:
   ```bash
   UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/env-alias \
   UV_CACHE_DIR=/tmp/.uv-cache-env-alias \
   UV_LINK_MODE=copy \
   uv run --extra dev env-alias --generator tests/manual/local_yaml_01.yml
   ```
2. Verify the output (the export lines) is printed to stdout.
3. Ensure no errors are reported in the logs (stderr).
