# SSH Bootstrap

Ensure a project-specific SSH key exists, then add it to a running SSH agent when the environment loads.

## Example

[exec](../definition-attributes/exec.md){: .feat .f-exec}
[name](../definition-attributes/name.md){: .feat .f-name}

```yaml
env-alias:

  BOOTSTRAP_SSH_KEY:
    name: null
    exec: 'mkdir -p "$HOME/.ssh/env-alias-example"; test -f "$HOME/.ssh/env-alias-example/bootstrap.key" || ssh-keygen -q -N "" -f "$HOME/.ssh/env-alias-example/bootstrap.key"'

  BOOTSTRAP_SSH_KEY_ADD:
    name: null
    exec: 'ssh-add -q "$HOME/.ssh/env-alias-example/bootstrap.key"'
```

Walkthrough:

1. `BOOTSTRAP_SSH_KEY` creates the directory and generates a key only when it is missing; it never
   deletes or replaces an existing identity.
2. `BOOTSTRAP_SSH_KEY_ADD` adds that key to a running SSH agent. It cannot start an agent or install
   the public key on a target for you; start an agent first and authorize the public key separately.
3. Both steps use `name: null`, so their output is discarded and no bootstrap variables are exported.
