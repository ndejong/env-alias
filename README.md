# Env Alias

[![PyPi](https://img.shields.io/pypi/v/env-alias.svg)](https://pypi.python.org/pypi/env-alias/)
[![Python Versions](https://img.shields.io/pypi/pyversions/env-alias.svg)](https://github.com/ndejong/env-alias/)
[![Build Status](https://github.com/ndejong/env-alias/actions/workflows/build-tests.yml/badge.svg)](https://github.com/ndejong/env-alias/actions/workflows/build-tests.yml)
[![Read the Docs](https://img.shields.io/readthedocs/env-alias)](https://env-alias.readthedocs.io)
![License](https://img.shields.io/github/license/ndejong/env-alias.svg)

Env Alias is an environment variable swiss-army-knife that enables loading complex collections 
of environment variables from a variety of sources only when you require them, thus reducing risks 
in working with sensitive environment values.

A variety of data-formats are supported including **JSON**, **YAML**, **Keepass**, **Ansible Vault**, 
**Plaintext** and **Ini**-config where these formats can be sourced from the local-filesystem, 
http-remote or generated through shell-command exec output.

For example setting an Ansible-vault password file and loading AWS access credentials from values stored 
in a git project based Keepass file: 
```yaml
env-alias:

  MYPROJECT_KEEPASS_FILE:
    name: null  # prevents this value being assigned into env
    exec: 'echo "$(git rev-parse --show-toplevel)/secrets/myproject-keepass.kdbx"'
  
  MYPROJECT_KEEPASS_PASSPHRASE:
    source: "<getpass>"  # obtain value from user-input using getpass method
    override: false  # if this env-value exists then skip setting again
    
  MYPROJECT_ANSIBLE_VAULT_PASSWORD:
    name: null  # prevents this value being assigned into env
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/ansible-vault-entry-name:Password"  # select an item from Keepass file
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_ANSIBLE_VAULT_PASSWORD"  # NB: see docs how this gets managed
    ansible_vault_password_file: true  # invoke special helper that renders an Ansible Vault password file

  AWS_SECRET_ACCESS_KEY:
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/aws-entry-name:Password"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"
    
  AWS_ACCESS_KEY_ID:
    source: "env:MYPROJECT_KEEPASS_FILE"
    selector: "myproject-name/aws-entry-name:Username"
    keepass_password: "env:MYPROJECT_KEEPASS_PASSPHRASE"

```

The above example sets the environment variable `MYPROJECT_KEEPASS_PASSPHRASE` with user input using 
the `getpass` Python module only if not already set (`override=false`).  This environment value is then 
used as the `keepass` passphrase to open a Keepass file where values are then selected and exported 
into the shell environment.

Substantially more complex env-alias definitions can be created.

By naming your env-aliases with an easy to remember prefix such as `env-` it is also possible to 
leverage shell **tab-completion** thus making it easier to find the env-alias definitions created 
for your project or other use-case situation.

## Features
Env Alias is enormously useful in working with large sets of environment variables from remote, encrypted 
or otherwise secured data-sources.
 
* Data sources: **local-files**, **http-remote** and stdout from an **exec** command-line.
* Source formats supported: **JSON**, **YAML**, **Keepass**, **Ansible Vault**, **Plaintext** and **Ini**-config.
* Select values using **jq** style selectors, **xpath** style selectors or **line-numbers**.
* 💥 Additional special handling for **Ansible Vault Password Files** that makes credential handling for **Ansible Vault** files substantially easier with reduced exposure risks. 💥     
* Self reference environment values in the definition file or from the existing system environment.
* Define variables with a `null` name to prevent them being exported into the system environment while still being available for self-reference within the env-alias definition; this is helpful when working with sensitive values that should not be available through the system environment.
* Ability to use `exec` commands to setup other project prerequisites or other project start conditions.
* Debug mode output to STDERR.
* Easy installation from PyPI.
* Plenty of documentation and examples - [https://env-alias.readthedocs.io](https://env-alias.readthedocs.io)

## Installation
Pip or pipx should be fine, we prefer pipx these days.
```shell
pipx install env-alias
```

## Usage
This tool is typically invoked using an entry in `.bash_aliases` with an entry of the form:-
```shell
source <(env-alias ~/projects/awesome/env-awesome-vars.yml)
```

This simple `.bash_aliases` one-line entry creates the alias `env-awesome-project` by inferring the 
alias-name from the filename, where this alias then invokes env-alias to set environment values 
defined in `env-awesome-project.yml` 

Alternatively, you might want to create the alias `awesome-envvars` which you could do as per - 
```shell
source <(env-alias awesome-envvars ~/projects/awesome/env-awesome-vars.yml)
```


## Project
* Github - [github.com/ndejong/env-alias](https://github.com/ndejong/env-alias)
* PyPI - [pypi.python.org/pypi/env-alias](https://pypi.python.org/pypi/env-alias/)
* ReadTheDocs - [env-alias.readthedocs.io](https://env-alias.readthedocs.io)

---
Copyright &copy; (2020-2024) Nicholas de Jong
