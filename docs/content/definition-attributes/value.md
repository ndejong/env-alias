# value

The `value` definition-attribute makes it possible to directly assign a value to an environment variable, it is 
the most straight forward use case.

Additionally, it is possible to reference other environment variables via the `env:` prefix as shown.  This can 
be helpful when the value needs to be dynamic and used in subsequent definition steps.

### Example - simple direct

```yaml
env-alias:
  
  MYPROJECT_ENVVAR:
    value: 'hello world'
```


### Example - by reference

```yaml
env-alias:
  
  MYPROJECT_ENVVAR:
    value: 'hello world'

  MYPROJECT_REFERENCED_ENVVAR:
    value: 'env:MYPROJECT_ENVVAR'
```
