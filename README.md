# Env Alias

[![PyPi](https://img.shields.io/pypi/v/env-alias.svg)](https://pypi.python.org/pypi/env-alias/)
[![Python Versions](https://img.shields.io/pypi/pyversions/env-alias.svg)](https://github.com/threatpatrols/env-alias/)
[![Build Status](https://github.com/threatpatrols/env-alias/actions/workflows/project-tests.yml/badge.svg)](https://github.com/threatpatrols/env-alias/actions/workflows/project-tests.yml)
![License](https://img.shields.io/github/license/threatpatrols/env-alias.svg)

Env Alias is an environment variable swiss-army-knife that lets you load complex collections of environment
variables from a variety of sources **only when you need them**, reducing the risk of working with sensitive values.

It loads values from local files, http(s) URLs, shell `exec` output, Keepass databases, Ansible Vault files — in
**JSON**, **YAML**, **Plaintext** and **INI** formats — and exports them into your shell as a one-shot sourced
command. Values are fetched lazily, on demand, when you invoke the alias, so secrets are never loaded until you
actually use them.

## Features

* **Data sources:** local files, `http(s)` URLs, `<getpass>`, `<stdin>`, KeePass, Ansible Vault, and stdout from `exec`.
* **Content formats:** JSON, YAML, INI, and plaintext.
* **Selectors:** dot, slash, and bracket paths for JSON/YAML; `<section>.<option>` for INI; line numbers for plaintext.
* **Ansible Vault Password File helper:** generates the executable password-file arrangement Ansible expects.
* **`env:NAME` references:** reuse one whole value from the process environment or an earlier definition.
* **Internal-only values:** `name: null` suppresses normal export to the calling shell while retaining the value for later definitions in the same run.
* **`exec` support:** run prerequisite or startup commands as part of a definition.
* **Terminal-only messages:** `value_to: <stderr>` writes to the terminal without polluting stdout.
* **`--debug` output:** written to STDERR; treat it as sensitive because it can contain secret material.
* **Multi-file invocation:** define many lazy aliases with one command.
* Easy installation from PyPI.

## Installation

Requires Python 3.10 or later.

```shell
pipx install env-alias
```

(Plain `pip install env-alias` works too.)

## How it works

There are two phases:

1. **Alias definition phase** — you add a line to `.bash_aliases` / `.bashrc`. When a new shell starts, `env-alias`
   prints one or more shell `alias` commands, which your shell sources. The aliases are lightweight placeholders —
   they do **not** load any secrets yet.
2. **Invocation phase** — when you actually run an alias (e.g. type `env-awesome`), it shells out to
   `env-alias --generator <file>`, which resolves the values and prints `export "VAR"='value'` lines that your
   shell sources. This is where the real (possibly slow, network/secret-fetching) work happens.

Because a child process can never modify your current shell, the command must be **sourced**. The standard wrapper is:

```shell
source <(env-alias ...)
# equivalent:
eval "$(env-alias ...)"
```

## Usage — `.bash_aliases`

### One alias, name inferred from the filename

```shell
source <(env-alias ~/projects/awesome/env-awesome-vars.yml)
```

This defines the alias `env-awesome-vars` (from the filename — note **hyphens are fine**), which when run loads the
environment defined in `env-awesome-vars.yml`.

### One alias, explicit name

```shell
source <(env-alias awesome-envvars ~/projects/awesome/env-awesome-vars.yml)
```

Defines the alias `awesome-envvars`. An explicit alias name may be followed by **only one** definition file.

### Many projects — one line, one alias per file

If you have ~20 project definition files, don't launch 20 `env-alias` processes at shell startup. Pass them all at
once — env-alias emits **one alias per file**, each lazily loading only its own file:

```shell
source <(env-alias \
  ~/.config/env-alias/env-proj-a.yml \
  ~/.config/env-alias/env-proj-b.yml \
  ~/.config/env-alias/env-proj-c.yml)
```

You can also pass a file pattern (glob):

```shell
source <(env-alias ~/.config/env-alias/env-*.yml)
```

One process at shell startup defines `env-proj-a`, `env-proj-b` and `env-proj-c` as independent lazily-loaded
aliases. This is the recommended pattern when you have many definitions.

### Tab-completion

Name your aliases with a common prefix such as `env-` so they group together for shell **tab-completion**.

## Example definition

```yaml
env-alias:

  MYPROJECT_KEEPASS_FILE:
    name: null                 # internal only — not exported
    exec: 'root="$(git rev-parse --show-toplevel)" && printf "%s/secrets/myproject-keepass.kdbx" "$root"'

  MYPROJECT_KEEPASS_PASSPHRASE:
    source: "<getpass>"        # prompt the user (getpass) when run
    override: false            # don't re-prompt if already set

  MYPROJECT_ANSIBLE_VAULT_PASSWORD:
    name: null
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/ansible-vault-entry-name:Password"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_ANSIBLE_VAULT_PASSWORD"
    ansible_vault_password_file: true   # render an Ansible Vault password file

  AWS_SECRET_ACCESS_KEY:
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/aws-entry-name:Password"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"

  AWS_ACCESS_KEY_ID:
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/aws-entry-name:Username"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"
```

`MYPROJECT_KEEPASS_PASSPHRASE` is prompted for via `getpass` but only if not already set (`override: false`), then
used to open the KeePass file so the AWS credentials and Ansible Vault password can be selected. The passphrase is
exported so it can be reused in the current shell; run `unset MYPROJECT_KEEPASS_PASSPHRASE` when finished.

## Definition attributes

Each definition uses a small set of attributes to describe how its value is generated. See
[the documentation](https://threatpatrols.github.io/env-alias/) for full detail:

| Attribute | Purpose |
|-----------|---------|
| `source` | Read a local file or HTTP(S) URL; `<getpass>`, `<stdin>`, and `env:VAR` are special sources |
| `parser` | Explicitly use `yaml`/`yml`, `json`, `ini`, or `none`; omitted content types are inferred |
| `selector` | Select a scalar from structured content, or a one-based line number from plaintext |
| `name` | Override the exported env-var name; `null` suppresses export to the calling shell |
| `value` | Set a direct value (or a whole-value `env:VAR` reference); bypasses parsing and selection |
| `exec` | Run a shell command; use its stdout as content |
| `override` | Whether to overwrite an existing env value (default `true`) |
| `keepass_password` | Password to open a Keepass `.kdbx` source |
| `ansible_vault_password` | Password for an Ansible Vault file |
| `ansible_vault_password_file` | Render an Ansible Vault password file |
| `value_to` | Also write a resolved value to `<stderr>`; combine with `name: null` for a terminal-only message |

## Debugging

Add `--debug` to see verbose diagnostics on STDERR:

```shell
source <(env-alias --debug env-awesome-vars.yml)
```

Note: `--debug` output can contain secret material — treat it as sensitive.

## Common issues & troubleshooting

* **Aliases not defined?** You must `source` (or `eval`) the output — a bare command only prints it.
* **`Empty or malformed definitions root 'env-alias'`** — your file's `env-alias:` key is empty/null. Add entries.
* **`keepassxc-cli` / `ansible-vault` not found** — install the respective binary and add it to `PATH`.
* See [Troubleshooting](https://threatpatrols.github.io/env-alias/troubleshooting/) for more.

## Security

**The `exec` attribute runs arbitrary shell commands (`shell=True`).** A malicious definition file can run any
command on your machine. Only use definition files you wrote or audited. See
[the security documentation](https://threatpatrols.github.io/env-alias/security/) for the full threat model.

## Project

* Docs — [threatpatrols.github.io/env-alias](https://threatpatrols.github.io/env-alias)
* PyPI — [pypi.python.org/pypi/env-alias](https://pypi.python.org/pypi/env-alias/)
* GitHub — [github.com/threatpatrols/env-alias](https://github.com/threatpatrols/env-alias)

This project was migrated from `github.com/ndejong/env-alias` to `github.com/threatpatrols/env-alias` in March 2025.
