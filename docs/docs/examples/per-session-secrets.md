# Per Session Secret

Prompt for a secret once per terminal session and reuse it from that shell without writing it to disk.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[override](../definition-attributes/override.md){: .feat .f-override}
[value](../definition-attributes/value.md){: .feat .f-value}

```yaml
env-alias:

  MYPROJECT_API_TOKEN:
    source: "<getpass>"    # prompt without echoing
    override: false        # don't re-prompt if already set this session

  MYPROJECT_API_USER:
    source: "<stdin>"      # plain (echoed) prompt
    override: false

  MYPROJECT_TOOL_TOKEN:
    value: 'env:MYPROJECT_API_TOKEN'

  MYPROJECT_TMP_DIR:
    value: "/tmp/myproject"
```

Walkthrough:

1. `MYPROJECT_API_TOKEN` — if it isn't already set, `getpass` prompts once (input is hidden); if it is
   already set, `override: false` skips it so you are only asked once per shell.
2. `MYPROJECT_API_USER` — same idea, but via a visible `<stdin>` read. Use `<getpass>` instead for a
   value that must not be echoed.
3. `MYPROJECT_TOOL_TOKEN` — copies the earlier token with a whole-value `env:` reference.
4. `MYPROJECT_TMP_DIR` — a plain in-line `value`.

`override: false` is the key to the whole pattern: it turns the prompt into a **once-per-session**
operation. The values are exported into the calling shell so later aliases can reuse them; they are also
inherited by child processes. Run `unset MYPROJECT_API_TOKEN MYPROJECT_TOOL_TOKEN` when finished.

!!! info "The `env:` reference"

    `env:` takes the *whole* remainder after the prefix as a single variable name, so
    `value: 'env:MYPROJECT_API_TOKEN'` copies `MYPROJECT_API_TOKEN`. It does **not** concatenate
    multiple variables (`env:A:B` is invalid). Use an intermediate definition for each value you need
    to combine.
