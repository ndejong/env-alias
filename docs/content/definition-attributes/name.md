# name

The `name` definition-attribute is used to name (or rename) the environment variable name that is otherwise 
taken from the env-alias definition key name.

More importantly, the `name` attribute can be set to `null` in which case the variable will be treated as an 
internal runtime only variable that does not get exposed into the environment; this is useful when passing 
secrets in-between definitions.


### Example - simple

```yaml
env-alias:
    DEFINITION_01:
        name: "MYPROJECT_ENV_VAR_01"
        value: "hello world a"
        
    DEFINITION_02:
        name: "MYPROJECT_ENV_VAR_02"
        value: "Hello World B"
```


### Example - hidden variable

The example below demonstrates using a `null` name for `MYPROJECT_HIDDEN_ENV_VAR` that does not get assigned into
the environment but can still be referenced in the subsequent `MYPROJECT_ENV_VAR` definition.

```yaml
env-alias:
    MYPROJECT_HIDDEN_ENV_VAR:
        name: null
        exec: "date +%s.%N"
        
    MYPROJECT_ENV_VAR:
        value: "env:MYPROJECT_HIDDEN_ENV_VAR"
```
