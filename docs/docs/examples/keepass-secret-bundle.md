# KeePass Secret Bundle

Set up one small KeePass unlocking scaffold and use it to supply any number of API keys or
credentials, each pulled from a single database without retyping the master password for every value.

## Example

[exec](../definition-attributes/exec.md){: .feat .f-exec}
[source](../definition-attributes/source.md){: .feat .f-src}
[name](../definition-attributes/name.md){: .feat .f-name}
[keepass_password](../definition-attributes/keepass-password.md){: .feat .f-keepass}
[selector](../definition-attributes/selector.md){: .feat .f-selector}
[override](../definition-attributes/override.md){: .feat .f-override}

```yaml
env-alias:

  SECRETS_KEEPASS_FILE:
    name: null
    exec: "cat ${HOME}/.config/keepass.file"

  SECRETS_KEEPASS_PASSWORD:
    name: null
    exec: "cat $(cat ${HOME}/.config/keepass.password)"

  CLOUD_API_TOKEN:
    source: "env:SECRETS_KEEPASS_FILE"
    selector: "cloud/portal:Password"
    keepass_password: "env:SECRETS_KEEPASS_PASSWORD"
    override: false

  CI_REGISTRY_TOKEN:
    source: "env:SECRETS_KEEPASS_FILE"
    selector: "devops/registry:Password"
    keepass_password: "env:SECRETS_KEEPASS_PASSWORD"
    override: false

  MONITORING_PUSH_KEY:
    source: "env:SECRETS_KEEPASS_FILE"
    selector: "ops/monitoring:Password"
    keepass_password: "env:SECRETS_KEEPASS_PASSWORD"
    override: false
```

Walkthrough:

1. `SECRETS_KEEPASS_FILE` and `SECRETS_KEEPASS_PASSWORD` are `exec`-based, `name: null` definitions
   that locate the KeePass database and its master password once. They are reusable as-is across every
   project because they only hold the *pointer-file* logic, not the secrets.
2. Each later value is then a self-contained lookup: `source` points at the database file and
   `keepass_password` supplies the master password, both via `env:` references to the scaffold. `selector`
   names the entry to pull (`group/title:Field`).
3. `override: false` means an already-exported token is left alone, so repeated invocations do not
   re-unlock the database for a value that is already set this session.
4. Add as many lookups as you like — every value is unlocked from the same one-time scaffold.

!!! info "Keepass setup"

    This pattern expects a small one-time setup: `${HOME}/.config/keepass.file` contains the path to
    your `.kdbx` database, and `${HOME}/.config/keepass.password` points to a file holding a KeePass
    key or password. `keepassxc-cli` must be on `PATH`. Env Alias keeps the database locked between
    invocations; it only reads the requested entry while the alias runs.
