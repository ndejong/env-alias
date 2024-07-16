# override

The `override` definition-attribute is used to skip setting an environment variable if an environment value 
already exists.

This is helpful when you only want to obtain user input once per terminal session.

### Example - override

```yaml
env-alias:

  MYPROJECT_USER_PASSWORD:
    source: "<getpass>"   # obtain value from user-input using getpass method
    override: false       # if this env-value exists then skip setting again

  MYPROJECT_USER_INPUT:
    source: "<stdin>"     # obtain value from user-input
    override: false       # if this env-value exists then skip setting again

```

