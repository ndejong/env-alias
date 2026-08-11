# exec

The `exec` definition-attribute runs a shell command and uses its STDOUT as the definition content.
Specify `parser` and `selector` when that output is structured. A nonzero exit status aborts generation
and reports the command's captured error output on STDERR.

!!! warning "Shell execution — understand the risk"

    The `exec` attribute runs an arbitrary shell command via `subprocess` with `shell=True`. This is
    by design, but a definition file is therefore as powerful as a shell script.

    **Threat model:**

    * **Untrusted YAML files:** Never run a definition file you did not author or audit. A malicious
      `exec` value can execute arbitrary code on your machine.
    * **Shared environments:** If multiple users share a definition file (e.g. in a team repo), any
      contributor can inject commands via `exec`. Review changes to definition files in code review.
    * **Downloaded definitions:** env-alias does not fetch definition files itself, but downloading an
      untrusted YAML file and then running env-alias against it has the same risk.

    **Mitigations:**

    * Treat env-alias definition files with the same caution as shell scripts.
    * Use the `source` attribute for HTTP(S) or local-file data when you do not need a shell command.
    * Set restrictive file permissions on definition files that contain sensitive `exec` commands.

## Example

```yaml
env-alias:
  PROJECT_ROOT:
    exec: 'git rev-parse --show-toplevel'

  BOOTSTRAP_CACHE:
    name: null
    exec: 'mkdir -p "$HOME/.cache/myproject"'
```

`PROJECT_ROOT` exports the command's single-line output. `BOOTSTRAP_CACHE` runs only for its side
effect; `name: null` discards the command's output instead of exporting a variable.
