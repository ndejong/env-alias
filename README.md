# Env Alias

[![PyPi](https://img.shields.io/pypi/v/env-alias.svg)](https://pypi.python.org/pypi/env-alias/)
[![Python Versions](https://img.shields.io/pypi/pyversions/env-alias.svg)](https://github.com/ndejong/env-alias/)
[![Build Status](https://github.com/ndejong/env-alias/actions/workflows/build-tests.yml/badge.svg)](https://github.com/ndejong/env-alias/actions/workflows/build-tests.yml)
[![Read the Docs](https://img.shields.io/readthedocs/env-alias)](https://env-alias.readthedocs.io)
![License](https://img.shields.io/github/license/ndejong/env-alias.svg)

Powerful helper utility to create shell alias commands to easily set collections of environment 
variables often with secret values from a variety of data-sources and data-formats.

Enables complex environment setups to be stored in source-control without secret values which makes 
it particularly useful in loading secret values into containerized service environments and developer 
environments alike.

## Features
* Data sources: local-file, http-remote, exec-stdout or directly-set
* Source file formats: `text`, `ini`, `json`, `yaml`
* Select using jq-style selectors, xpath selectors or line-numbers
* Reference other env values within configuration
* Content-Type detection for http-remote data-sources to automatically assign appropriate parser
* Run exec helper commands without content assignment for creating setups 
* Debug mode output to STDERR
* Easy installation using PyPI `pip`
* Plenty of documentation and examples - https://env-alias.readthedocs.io

## Installation
```shell
user@computer:~$ pip install env-alias
```

## Command Line Usage
This tool is typically invoked via an entry in `.bash_aliases` with an entry in the form:-
```shell
eval $(env-alias env-project-awesome ~/path-to/project-awesome-alias.yml)
```

This simple one-liner creates a command alias in the name `env-project-awesome` that subsequently invokes
an alias-generator that gives effect to the `.yml` configurations(s). 

By naming your alias commands with a common prefix such as `env-` it also becomes possible to leverage 
shell tab-completion to quickly find aliases that implement the environment settings for your project, 
use-case or other situation.

This mechanism is enormously useful in working with large sets of environment variables from encrypted 
or otherwise secured data-sources which means an environment configuration can be easily committed to 
source control without the secret values.

Be sure to review the examples that make the benefits of this arrangement clear.

## Project
* Github - [github.com/ndejong/env-alias](https://github.com/ndejong/env-alias)
* PyPI - [pypi.python.org/pypi/env-alias](https://pypi.python.org/pypi/env-alias/)
* ReadTheDocs - [env-alias.readthedocs.io](https://env-alias.readthedocs.io)

---
Copyright &copy; 2021 Nicholas de Jong
