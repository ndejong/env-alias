# name

The `name` definition-attribute changes the environment variable name that would otherwise come from the
definition key.

Set `name: null` to calculate a value without emitting an `export` for the calling shell. The value
remains available to later definitions and child `exec` processes during the same generator run, which
makes it useful for intermediate paths and secrets.


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

The example below keeps `MYPROJECT_HIDDEN_ENV_VAR` out of the calling shell while making it available
to the subsequent `MYPROJECT_ENV_VAR` definition.

```yaml
env-alias:
    MYPROJECT_HIDDEN_ENV_VAR:
        name: null
        exec: "date +%s.%N"
        
    MYPROJECT_ENV_VAR:
        value: "env:MYPROJECT_HIDDEN_ENV_VAR"
```
