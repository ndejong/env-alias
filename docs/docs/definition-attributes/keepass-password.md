# keepass_password

Use `keepass_password` with a KeePass `.kdbx` file source. Env Alias requires `keepassxc-cli` on
`PATH` and passes the database password to it through STDIN without invoking a shell.

For KeePass sources, `selector` has the form `<entry-path>:<attribute>`. The attribute can be
`Username`, `Password`, or another KeePass entry attribute; attribute names are case-sensitive.

## Example

```yaml
env-alias:

  MYPROJECT_KEEPASS_PASSPHRASE:
    name: null
    source: "<getpass>"

  MYPROJECT_SECRET_VALUE:
    source: "~/.config/myproject/secrets.kdbx"
    selector: "team/ci:Username"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"
```

`MYPROJECT_KEEPASS_PASSPHRASE` is internal to the generator run, while
`MYPROJECT_SECRET_VALUE` is exported with the selected KeePass attribute.
