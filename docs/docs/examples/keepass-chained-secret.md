# KeePass + Chained Secret

Prompt once during an alias invocation to unlock a KeePass database, then use the selected secret to
generate an Ansible Vault password file.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[name](../definition-attributes/name.md){: .feat .f-name}
[keepass_password](../definition-attributes/keepass-password.md){: .feat .f-keepass}
[selector](../definition-attributes/selector.md){: .feat .f-selector}
[ansible_vault_password](../definition-attributes/ansible-vault-password.md){: .feat .f-ansible}
[ansible_vault_password_file](../definition-attributes/ansible-vault-password-file.md){: .feat .f-ansible}

```yaml
env-alias:

  MYPROJECT_KEEPASS_PASSPHRASE:
    name: null
    source: "<getpass>"

  MYPROJECT_VAULT_PASSWORD:
    name: null
    source: "~/secrets/myproject.kdbx"
    selector: "team/ansible-vault:Password"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_VAULT_PASSWORD"
    ansible_vault_password_file: true
```

Walkthrough:

1. `MYPROJECT_KEEPASS_PASSPHRASE` prompts with hidden input and stays internal to this generator run.
   `keepassxc-cli` must be installed and available on `PATH`.
2. `MYPROJECT_VAULT_PASSWORD` opens the KeePass database and selects the `Password` attribute from
   `team/ansible-vault`. It is also internal-only and only feeds the next definition.
3. `ANSIBLE_VAULT_PASSWORD_FILE` renders an executable password file. The helper exports the vault
   password under a generated environment-variable name so Ansible can read it; unset that generated
   variable after the session if it is no longer needed.
