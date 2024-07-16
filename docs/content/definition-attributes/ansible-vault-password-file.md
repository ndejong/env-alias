# ansible_vault_password_file

The `ansible_vault_password_file` definition-attribute is a special attribute that causes a standard Ansible Vault 
password-file to be generated as per [docs.ansible.com](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_VAULT_PASSWORD_FILE) documentation.

When this is used to set Ansible variable `ANSIBLE_VAULT_PASSWORD_FILE` you gain the ability to easily invoke
ansible-vault without further Ansible configuration or other Ansible environment settings.

### Details

Of note is that the ansible-password-file rendering uses random file names and hash-of-source-name to create consistent 
but difficult to guess environment names making it harder to target specific environment values. 

```commandline
$ env | grep ANSIBLE_VAULT_PASSWORD_FILE
ANSIBLE_VAULT_PASSWORD_FILE=/tmp/igxrsfnrsxig

$ cat /tmp/igxrsfnrsxig
#!/bin/sh
echo "${E25AF8C1096A}"

$ env | grep E25AF8C1096A 
E25AF8C1096A=zPrT1z8yYTBV5q5l7jahGoQf79fcu9qtD4ERM3wB
```

In the above example -

* The env-var `ANSIBLE_VAULT_PASSWORD_FILE` points to a random filename `/tmp/igxrsfnrsxig` located in the system temp path
* The Ansible password-file is a standard format executable that echos out another environment value as per Ansible [documentation](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_VAULT_PASSWORD_FILE)
* The environment name `E25AF8C1096A` gets generated based on a salted SHA256 of the source attribute name (not the value itself)
* Finally, the value for the vault-password is exposed on the environment variable `E25AF8C1096A`  

The above is achieved using an env-alias definition as simple as -
```yaml
  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "some-secret-value"
    ansible_vault_password_file: true
```

!!!warning

    Typically, the `ansible_vault_password` value should never be set using an in-the-clear value as shown above, you 
    should use prior steps to obtain this value safely/securely such as from user-input using `<getpass>` or load 
    from a Keepass file or other appropriate mechanism.
