# Common Issues

## Aliases are not defined when the shell starts

`source <(env-alias file.yml)` must be executed in a **sourced** context (`.bash_aliases`, `.bashrc`, or a terminal).
If you run it as a plain command the aliases are only printed, not installed. Use either form:

```shell
source <(env-alias env-awesome.yml)
# or
eval "$(env-alias env-awesome.yml)"
```

Remember: the `source <( ... )` (or `eval "$( ... )"`) wrapper is **required** — a child process cannot define
aliases or set env vars in your current shell.

## "Empty or malformed definitions root 'env-alias'"

Your definition file's `env-alias:` key has no entries, or resolves to an empty/null value. For example a file that
contains only:

```yaml
env-alias:
```

parses with a null root and is rejected. Add at least one definition. A truly empty file (no `env-alias:` key at
all) reports "Unable to locate top-level definitions root 'env-alias'".

## "Unable to locate required binary 'keepassxc-cli'" / "'ansible-vault'"

Keepass and Ansible Vault sources require the `keepassxc-cli` and `ansible-vault` executables respectively.
Install them (e.g. `apt install keepassxc ansible`) and ensure they're on `PATH`.

## Remote (`http` / `https`) sources fail

* The URL scheme must be `http://` or `https://`. Other schemes are rejected outright (`Rejected URL with disallowed scheme`).
* Responses are limited to a **10 MB** maximum.
* The HTTP (GET) timeout is **30 seconds**.
* A non-UTF-8 body may fail to decode.

## "Invalid alias name …"

Alias names (unlike environment variable names) may contain hyphens, e.g. `env-awesome-vars`. The name must still
start with a letter or underscore and contain only letters, digits, underscores and hyphens. When an explicit alias
name is given, only **one** definition file may follow it — pass multiple files without an explicit alias so each
file's name is inferred:

```shell
# valid: one alias per file, inferred names
source <(env-alias env-a.yml env-b.yml env-c.yml)

# error: explicit alias + multiple files is ambiguous
source <(env-alias myalias env-a.yml env-b.yml)
```

## `--debug` shows unexpected/redacted output

`--debug` (or `ENVALIAS_DEBUG=true`) writes verbose diagnostics to **stderr**, including source paths, selectors
and rendered command lines. Known secret values are shown as `<redacted>`, but very short secrets (2 chars or less)
are not, and an `exec:` line may contain a secret after `env:` substitution. Treat `--debug` output as sensitive —
see [Security](security.md).

## A structured source says a selector is required

`json`, `yaml`, and `ini` content must use a `selector`. JSON/YAML selectors use dot, slash, or bracket
paths; INI selectors use `<section>.<option>`. If you need the complete raw file instead, set
`parser: none` and omit the selector.

## `value_to: <stdout>` fails with a "removed" error

`value_to: <stdout>` was **removed in 0.7.0**. env-alias's stdout is always sourced by your shell
(`source <(env-alias ...)`), so writing a raw value there meant it was executed as shell code — broken output, and
a command-execution risk if the value contained shell syntax. A definition using `<stdout>` / `<STDOUT>` now fails
with an error that tells you to use `value_to: <stderr>` instead. Change:

```yaml
value_to: "<stdout>"   # removed
```
to
```yaml
value_to: "<stderr>"   # writes the same content to the terminal, safely
```

`value_to: <stderr>` works under `source <(...)` because stderr is never consumed by the shell.

## An `exec:` command fails with a nonzero exit

`exec` runs the command via the shell with `shell=True`; any nonzero exit code aborts the run and prints the captured
stdout/stderr (truncated). Use `--debug` to see exactly which command ran. Remember `exec` runs **arbitrary shell
commands** — only run definition files you trust (see [Security](security.md)).

## Tests need network or external binaries

`make test` excludes tests marked `network` and `slow`. Use `make test-all` to include them. The
KeePass and Ansible Vault integrations need `keepassxc-cli` and `ansible-vault` on `PATH`; install those
tools when you need to exercise the integrations locally.
