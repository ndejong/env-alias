# keepass_password

The `keepass_password` definition-attribute is used to send a password through keepass-cli when opening a Keepass
file that hence makes it possible select values inside Keepass files. 


### Example - keepass

```yaml
env-alias:

  MYPROJECT_KEEPASS_PASSPHRASE:
    source: "<getpass>"  # obtain value from user-input using getpass method
    override: false  # if this env-value exists then skip setting again
    
  MYPROJECT_KEEPASS_FILE:
    name: null  # prevent this value being assigned into env with this name
    exec: 'echo "$(git rev-parse --show-toplevel)/secrets/myproject-keepass.kdbx"'
    
  MYPROJECT_SECRET_VALUE:
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "keepass-folder-name/keepass-entry-name:Password"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"
```

The example above demonstrates how it is possible to collect a keepass password into an environment variable
with user-input and use this to open and access contents within a Keepass file.

**NB:** case-sensitive "Password" expression in the selector expression, similarly, "Username" is case-sensitive too.


## Under the hood
Under the hood env-alias wraps a command line to exec a keepass-cli command as shown -

```python
random_envvar = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(16))
os.environ[random_envvar] = password

command_line = (
    f' printf "${"{" + random_envvar + "}"}" | "{keepassxc_cli}" show '
    f'--quiet --show-protected --attributes "{keepass_attribute}" "{str(filename)}" "{keepass_path}"'
)

execute_content = EnvAliasSource.execute(command_line)
os.unsetenv(random_envvar)
```
