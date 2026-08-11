# ansible_vault_password

The `ansible_vault_password` definition-attribute supplies the password for an Ansible Vault source
or to the `ansible_vault_password_file` helper. Reading an encrypted vault requires `ansible-vault`
on `PATH`.

## Read a Vault value

```yaml
env-alias:

    EXAMPLE_ANSIBLE_VAULT_PASSWORD:
        name: null
        source: "<getpass>"

    EXAMPLE_VALUE:
        source: "~/My Files/ansible-vault-datafile.vault"
        selector: "all/vars/vault/my_example_value"
        ansible_vault_password: "env:EXAMPLE_ANSIBLE_VAULT_PASSWORD"
```

The password is prompted for without echoing and is not exported to the calling shell under
`EXAMPLE_ANSIBLE_VAULT_PASSWORD`. It remains available inside the generator long enough to decrypt the
Vault, then `selector` chooses `EXAMPLE_VALUE` from the resulting YAML.

## Generate an Ansible password file (full example)

`ansible_vault_password` is also the password half of the `ansible_vault_password_file` pair. Set
`ansible_vault_password_file: true` alongside it on a definition to generate the executable password
file that Ansible reads from its `ANSIBLE_VAULT_PASSWORD_FILE` setting.

Because both features consume the same `ansible_vault_password` value, you can supply the password
once and *chain* it into however many definitions need it. Here is the complete example: one internal
password, used both to decrypt a Vault value and to build the password file.

```yaml
env-alias:

  MYPROJECT_VAULT_PASSWORD:
    name: null
    source: "<getpass>"

  # Step 1: generate the password file Ansible will read.
  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_VAULT_PASSWORD"
    ansible_vault_password_file: true

  # Chain step 2: decrypt a Vault value with that same password.
  MYPROJECT_DATABASE_PASSWORD:
    source: "~/secrets/myproject.vault"
    selector: "all/vars/database/password"
    ansible_vault_password: "env:ANSIBLE_VAULT_PASSWORD_FILE"
```

How the chain fits together:

1. `MYPROJECT_VAULT_PASSWORD` — captures the password once with `getpass`. `name: null` keeps it
   internal, so it is not exported under its own name.
2. `ansible_vault_password: "env:MYPROJECT_VAULT_PASSWORD"` — passes that captured value into both
   following definitions. This is the single thread the whole chain hangs on: change the source once
   and every definition in the chain uses the new value.
3. `ansible_vault_password_file: true` — for `ANSIBLE_VAULT_PASSWORD_FILE`, turns the same password
   into the password file. Env Alias exports `ANSIBLE_VAULT_PASSWORD_FILE` (the file path) plus a
   generated environment variable holding the password, so Ansible can obtain it without prompting.
4. `ansible_vault_password` on the Vault-reading definition — decrypts the vault with the same value,
   so only one password is ever needed for the session.

After sourcing the output, both the file path and the decrypted value are available together:

```console
$ eval "$(env-alias --generator myproject.yml)"
$ echo "$ANSIBLE_VAULT_PASSWORD_FILE"
/tmp/rlykdcpulv9z
$ echo "$MYPROJECT_DATABASE_PASSWORD"
<value decrypted from the vault>
```

For the generated password file's lifecycle and security details, see
[ansible_vault_password_file](ansible-vault-password-file.md).
