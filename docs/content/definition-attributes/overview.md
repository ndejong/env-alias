# Overview

Env Alias definition files are YAML format files that define how the value for each environment variable is generated.

* All Env Alias definition files MUST have an `env-alias` top-level root.
* Environment variable names are defined by their key name, or their `name` attribute.
* Each environment-variable definition uses attributes that define how their values are 
  generated or obtained.

Conceptually, values for the environment variables are generated in three steps -

 1. Content from source: this can be from the local-filesystem, exec-command, remote-http, in-line etc.
 2. Parse the source content: serializing the content from its respective format YAML, JSON, INI, TEXT etc.
 3. Select the item from the parsed content: using a `jq` style selector (or xpath selector) select the value required. 

Modifiers and special cases (e.g. Ansible Password Files) are possible, however the above 1,2,3 steps are usual.

The following definition attributes are available -

* [**source**](../source) - defines a source of content to be sent to the parser.  The `source` attribute supports 
  some special values including `<getpass>` that invokes the Python getpass module, regular `<stdin>` that does what 
  you'd expect from STDIN, the prefix `env:` can be used to import the source definition from another environment 
  variable.  Source values beginning with `http` are treated as remote-http that invoke a GET request to retrieve.

* [**parser**](../parser) - the parser (or deserializer) is automatically estimated based on source filename 
  extensions or the `Content-Type` header (if http-remote) and defaults to TEXT if nothing is determined.  This 
  behaviour is easily overridden by defining `ini`, `yaml`, or `json` as the parser; additionally, a `none` parser is
  available that does a raw pass-through without any parsing.

* [**selector**](../selector) - the selector provides the ability to "select" a value from the parsed content.  Selectors 
  support basic forms of dot-notation (eg: `foo.0.bar`), brace-notation (eg: `foo[0]bar`) and slash-notation (eg: 
  `foo/0/bar`).  Text files support line-number selectors for the full line only.  Defining the selector as `null` 
  prevents the environment variable from being exported into the system environment that is similar to setting 
  the `name` as null.

* [**name**](../name) - override the definition key-name and use this name instead; defining the name as `null` (without 
  quotes) causes the variable to become internal-only within the definition file and will not be exported into the 
  system environment.

* [**value**](../value) - directly set the value in-line; values prefixed with `env:` can be used to import values from 
  another environment variable. 

* [**exec**](../exec) - defines a command-line to exec where the STDOUT is returned as the source content; any nonzero 
  exit-code will raise an exception that will exit with an error from the command-line STDERR output. 

* [**override**](../override) - a true/false attribute that defines if Env Alias will override any existing environment 
  value; by default set to `True`.

* [**keepass_password**](../keepass-password) - used to define a password to open a Keepass database `.kdbx` file as 
  a `source` definition; Additionally, a `selector` in the form `group/subgroup/entryname:Password` is required to 
  obtain the desired Keepass value.

* [**ansible_vault_password**](../ansible-vault-password) - used to define a password to open an Ansible Vault 
  file; this attribute can be used _either_ to open and select values from an Ansible Vault -or- invoke the special 
  ansible-vault-password-file helper.

* [**ansible_vault_password_file**](../ansible-vault-password-file) - a true/false attribute that is used together 
  with the `ansible_vault_password` attribute to automatically create an [Ansible Vault Password File](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_VAULT_PASSWORD_FILE) (executable 
  file style) setups; 💥 this super helpful and a favorite feature! 💥
