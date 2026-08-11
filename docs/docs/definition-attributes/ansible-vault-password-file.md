# ansible_vault_password_file

`ansible_vault_password_file` is a boolean that generates a special executable script for Ansible
that emits the supplied `ansible_vault_password` value that makes Ansible Vault automation very
easy to handle.

## What it does

Setting `ansible_vault_password_file: true` on a definition (alongside `ansible_vault_password`)
exports two things:

* `ANSIBLE_VAULT_PASSWORD_FILE` (or the `name` you choose) — the path to the generated executable
  script.
* A generated environment variable holding the raw password, which that script prints so Ansible can
  read it.

The script path and generated variable name are derived deterministically from the password. Env Alias
writes the script to the system temporary directory with owner-only permissions, reuses it for the
same password, and does not remove it automatically.

## Example

```yaml
env-alias:
  MYPROJECT_VAULT_PASSWORD:
    name: null
    source: "<getpass>"

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_VAULT_PASSWORD"
    ansible_vault_password_file: true
```

For the full example of chaining `ansible_vault_password` into both the password file and a Vault
read, see [ansible_vault_password](ansible-vault-password.md).

!!! warning

    Do not put a vault password directly in the definition file. Use `<getpass>`, KeePass, or another
    appropriate source. Treat the resulting shell environment and temporary password-file path as
    sensitive, and unset the generated variable when the Ansible session is finished.
