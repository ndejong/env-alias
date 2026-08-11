# Terminal Messages

Send a status message to STDERR while the environment loads, without polluting the shell output.

## Example

[name](../definition-attributes/name.md){: .feat .f-name}
[value](../definition-attributes/value.md){: .feat .f-value}
[value_to](../definition-attributes/value-to.md){: .feat .f-valueto}

```yaml
env-alias:

  WELCOME:
    name: null
    value: "Loaded checkout environment"
    value_to: "<stderr>"

  CACHE_HINT:
    name: null
    value: "Tip: run 'make clean' to reset"
    value_to: "<stderr>"
```

Walkthrough:

1. Each definition's value is written to **STDERR** (which your shell ignores when sourcing), so you
   see the message on your terminal while the real `export` lines still load cleanly into your
   environment.
2. Because `name: null`, nothing is exported under these names — they only produce terminal output.

Never use `value_to` to reveal a secret: STDERR can be captured by terminals, CI systems, and logs.
