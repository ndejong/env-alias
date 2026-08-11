# value_to

The `value_to` definition-attribute writes the resolved value to **STDERR**. It is additive: a normal
definition still emits its usual shell `export`. Combine it with `name: null` when the value should be a
terminal-only status message.

Do not use `value_to` to reveal secrets. STDERR can be captured by terminals, CI systems, and logs.

## Example — to STDERR

```yaml
env-alias:

  EXAMPLE_STDERR:
    name: null
    value: "This is a message that will get sent to STDERR"
    value_to: "<stderr>"
```

The message is written to STDERR, which the shell never sources, so it is displayed in your terminal without
interfering with stdout. Because the definition uses `name: null`, it does not export `EXAMPLE_STDERR`.

## `value_to: <stdout>` was removed (0.7.0)

**`value_to: <stdout>` is no longer supported.** It was removed because env-alias's stdout is *always* sourced by
your shell (`source <(env-alias ...)`), so anything written there is executed as shell code. Writing a raw,
unquoted value to stdout therefore produced broken output — and could execute arbitrary commands if the value
contained shell syntax.

If you still have `<stdout>` (or `<STDOUT>`) in a definition, env-alias now fails with a clear error like:

```
Invalid definition for 'EXAMPLE': ... "'value_to: <stdout>' was removed because it wrote raw, unquoted text into
the stream your shell sources. Use 'value_to: <stderr>' to send a message to the terminal instead."
```

Simply change `value_to: "<stdout>"` to `value_to: "<stderr>"` to send the same content to the terminal safely.
