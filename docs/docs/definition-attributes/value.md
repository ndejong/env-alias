# value

The `value` definition-attribute assigns content directly. It bypasses `source`, `parser`, and
`selector`, so use it for a literal value or a whole-value `env:` reference.

`value: "env:NAME"` looks up `NAME` in the process environment first, then in an earlier definition.
The reference must occupy the entire value; it does not concatenate multiple variables. Definitions are
evaluated in order, so place the value-producing definition before its consumer. See
[source](source.md#env-references) for the complete `env:` rules.

### Example - direct value

```yaml
env-alias:
  
  MYPROJECT_ENVVAR:
    value: 'hello world'
```


### Example - reference an earlier definition

```yaml
env-alias:
  
  MYPROJECT_ENVVAR:
    value: 'hello world'

  MYPROJECT_REFERENCED_ENVVAR:
    value: 'env:MYPROJECT_ENVVAR'
```
