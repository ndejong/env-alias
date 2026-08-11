# Debugging

Add `--debug` to see diagnostic logs on STDERR while the alias is generated:

```shell
source <(env-alias --debug ~/projects/awesome/env-awesome-vars.yml)
```

You can also set `ENVALIAS_DEBUG=true` before invoking the alias. Debug output can include definition
paths, selectors, command lines, and resolved values. Treat it as sensitive: do not paste it into an
issue tracker or chat without reviewing and redacting it first. See [Security](security.md) for details.
