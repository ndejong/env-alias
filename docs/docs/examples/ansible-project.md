# Ansible Vault Password File

Show how `ansible_vault_password` feeds `ansible_vault_password_file` to give an Ansible session a
vault password without typing it or storing it in the definition file. It also contrasts the helper
with the hand-rolled `exec` approach it replaces.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[name](../definition-attributes/name.md){: .feat .f-name}
[value](../definition-attributes/value.md){: .feat .f-value}
[ansible_vault_password](../definition-attributes/ansible-vault-password.md){: .feat .f-ansible}
[ansible_vault_password_file](../definition-attributes/ansible-vault-password-file.md){: .feat .f-ansible}

```yaml
env-alias:

  MYPROJECT_VAULT_PASSWORD:
    name: null
    source: '~/.credentials/myproject/ansible-vault.pass'

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_VAULT_PASSWORD"
    ansible_vault_password_file: true

  ANSIBLE_TIMEOUT:
    value: '30'
```

Walkthrough:

1. `MYPROJECT_VAULT_PASSWORD` reads the password from a local file and, because `name: null`, keeps it
   internal to this run. Definitions evaluate in order, so this value is ready for the next step.
2. `ANSIBLE_VAULT_PASSWORD_FILE` is the pair. `ansible_vault_password` receives the password and
   `ansible_vault_password_file: true` turns that same password into the two exports Ansible reads:
   * `ANSIBLE_VAULT_PASSWORD_FILE`, pointing at an executable script in the temp directory; and
   * a generated environment variable (derived from the password) holding the raw value, which that
     script prints.
3. `ANSIBLE_TIMEOUT` is a plain in-line `value`, set alongside the rest.

### The pairing in use

After sourcing the output, Ansible already has `ANSIBLE_VAULT_PASSWORD_FILE` set, so vault-protected
commands work without `--ask-vault-pass`:

```console
$ eval "$(env-alias --generator myproject.yml)"
$ echo "$ANSIBLE_VAULT_PASSWORD_FILE"      # the executable script Env Alias generated
/tmp/rlykdcpulv9z
$ ansible-playbook -i inventory/production site.yml
```

When Ansible needs the password it runs that script, which reads the generated environment variable.
Nothing writes the password to the definition file, and the only place the raw value reaches the shell
is that generated variable, so keep the session environment private and `unset` it when finished.

### Before the helper

The helper automates work that is otherwise done by hand. Without it the same result took three
definitions: point `ANSIBLE_VAULT_PASSWORD_FILE` at a path, then `exec` a script that prints the
password from an exported variable:

```yaml
env-alias:

  MYPROJECT_VAULT_PASSWORD:
    name: null
    source: '~/.credentials/myproject/ansible-vault.pass'

  ANSIBLE_VAULT_PASSWORD_FILE:
    value: '/tmp/myproject_vault'            # hand-managed path

  ANSIBLE_VAULT_PASSWORD_ECHO_FILE:
    name: null
    exec: 'printf "#!/bin/sh\n" > /tmp/myproject_vault; printf "echo \${MYPROJECT_VAULT_PASSWORD}\n" >> /tmp/myproject_vault; chmod 700 /tmp/myproject_vault'
    selector: null
```

`ansible_vault_password` + `ansible_vault_password_file` collapse those three definitions into one,
with the path, the generated variable name, and the executable `chmod 700` script all handled for you.
