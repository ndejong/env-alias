# ansible_vault_password

The `ansible_vault_password` definition-attribute is used to define a password used to open an Ansible Vault file.

This value can be used in two contexts -

1. Can be used as an ansible-vault-file `source` to then select an item for a regular env-alias 
   definition - see the **Regular usage** below.
2. Can be used with the `ansible_vault_password_file` attribute that invokes a special helper for generating Ansible 
   Vault password-files; this is super-helpful when working with Ansible, see the **Special helper usage** below.


## Regular usage
```yaml
env-alias:

    EXAMPLE_ANSIBLE_VAULT_PASSWORD:
        name: null
        source: "<getpass>"
        override: false  # if this env-value exists then skip setting again

    EXAMPLE_VALUE:
        source: "~/My Files/ansible-vault-datafile.vault"
        selector: "all/vars/vault/my_example_value"
        ansible_vault_password: "env:EXAMPLE_ANSIBLE_VAULT_PASSWORD"
```
The example above -

* the ansible-password variable input is taken from user input using Python getpass.
* the user-input is _not_ exported into the system environment (`name: null`) and only exists internally within env-alias. 
* the user-input is skipped if the env-value is already set.
* the environment value `EXAMPLE_VALUE` is set using an item located at `all/vars/vault/my_example_value` within the 
  ansible-vault file `ansible-vault-datafile.vault`. 


## Special helper usage
The special Ansible helper is invoked by setting `ansible_vault_password_file` to true. 

This special helper makes working with Ansible Vault files considerably easier and tidier by self generating the 
required (executable) Ansible Vault Password File.

The helper also generates "hard-to-guess" filenames and environment values that are derived from multiple sha256 
rounds of the password with salt added. See the [docs](/definition-attributes/ansible_vault_password_file) for more 
details on this mechanism.

```yaml
env-alias:

    EXAMPLE_ANSIBLE_VAULT_PASSWORD:
        name: null
        source: "<getpass>"

    ANSIBLE_VAULT_PASSWORD_FILE:
        ansible_vault_password: "env:EXAMPLE_ANSIBLE_VAULT_PASSWORD"
        ansible_vault_password_file: true
```

The example above -

* the ansible-password variable input is taken from user input using Python `getpass`.
* the user-input is _not_ exported into the system environment (`name: null`) and only exists internally within env-alias. 
* the environment variable `ANSIBLE_VAULT_PASSWORD_FILE` is set to a value that points to a generated executable file
  that uses random file-names and hard-to-guess variable-names.

This arrangement then allows the user to interact with `ansible-vault` without any further configuration or effort to 
manage the credential.  You may additionally choose to store the Ansible Vault password in a Keepass database that can 
be easily chained together here.
