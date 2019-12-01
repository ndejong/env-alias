# Env Alias

[![PyPi](https://img.shields.io/pypi/v/env-alias.svg)](https://pypi.org/project/env-alias/)
[![Build Status](https://api.travis-ci.org/ndejong/env-alias.svg?branch=master)](https://api.travis-ci.org/ndejong/env-alias)
[![PyPi](https://img.shields.io/github/license/ndejong/env-alias.svg)](https://github.com/ndejong/env-alias)

Helper utility to create shell alias commands that easily set collections of environment variables often with secret
values from a variety of data-sources and data-formats.

Typically this tool is invoked via an entry in `.bash_aliases` with an entry in the form
```bash
eval $(env-alias my-alias-name ~/path-to/my-alias-name-config-file.yml)
```

Where this  example would establish a shell alias command for the alias `my-alias-name` that then invokes the
`env-alias-generator` with configuration from `~/path-to/my-alias-name-config-file.yml`

This provides an appropriate mechanism to manage large sets of environment variables with values from encrypted or 
otherwise secured data-sources through one simple alias command using a configuration file that can be safely committed 
to source control without exposing secret values.

## Features
* Data sources: direct-setting, exec-stdout, local-file, http-remote
* Source file formats: `text`, `ini`, `json`, `yaml`
* Select using line-numbers, jq-style or xpath-style selections
* Reference other env values within configuration
* Content-Type detection for http-remote data-sources to automatically assign appropriate parser
* Exec helper commands without env-variable assignment
* Debug mode output to STDERR

## Install
#### via PyPi
```bash
pip3 install env-alias
```

#### via Source
```bash
git clone https://github.com/ndejong/env-alias
cd env-alias
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 setup.py clean
python3 setup.py test
python3 setup.py install
```

## Project
* [github.com/ndejong/env-alias](https://github.com/ndejong/env-alias)

## Configuration Samples
The following examples are presented within the provided [`env-alias-sample.yml`](https://github.com/ndejong/env-alias/blob/master/samples/env-alias-sample.yml) file.

#### local_text_01
Assign the env `local_text_01` to the value of the 1st line of text in `/tmp/textfile.txt`
```yaml
local_text_01:
    source: '/tmp/textfile.txt'
```

#### local_text_02
Assign the env `local_text_02` to the value of the 2nd line of text in `/tmp/textfile.txt`
```yaml
local_text_02:
    source: '/tmp/textfile.txt'
    selector: 2
```

#### local_text_03
Assign the env `local_text_03` using the 1st line of text in the text file; text file format used as default file format
```yaml
local_text_03:
    source: '/tmp/textfile_without_extension'
```

#### local_text_04
Assign the env `local_text_04_override_name` using the 1st line of text in the file and use a different variable name
```yaml
local_text_04:
    name: 'local_text_04_override_name'
    source: '/tmp/textfile.txt'
```

#### local_text_05
Assign the env `local_text_05` using the 1st line of text in the file specified by env variable `${some_env_with_a_filename}`
```yaml
local_text_05:
    source: 'env:some_env_with_a_filename'
```

#### local_text_06
Assign the env `local_text_06` using the 1st line of text in the file and force the "text" content parser which is the default parser anyway
```yaml
local_text_06:
    source: '/tmp/textfile.txt'
    parser: 'text'
```

#### local_ini_01
Assign the env `local_ini_01` from the [foo] section under the [bar] option value; parser determined by filename extension
```yaml
local_ini_01:
    source: '/tmp/inifile.ini'
    selector: 'foo.bar'
```

#### local_ini_02
Assign the env `local_ini_02` from the [foo] section under the [bar] option value; parser manually set since it can not be determined via filename extension
```yaml
local_ini_02:
    source: '/tmp/file_without_ini_extension'
    selector: 'foo.bar'
    parser: 'ini'
```

#### local_json_01
Assign the env `local_json_01` from the JSON content using an xpath-style path selector to the desired value
```yaml
local_json_01:
    source: '/tmp/jsonfile.json'
    selector: 'foo.0.bar'
```  

#### local_json_02
Assign the env `local_json_02` from the JSON content using a jq-style path selector to the desired value
```yaml
local_json_02:
    source: '/tmp/jsonfile.json'
    selector: '.foo[1]bar'
```

#### local_json_03
Assign the env `local_json_03` from the JSON content using an xpath-style path selector to the desired value; set the JSON parser
```yaml
local_json_03:
    source: '/tmp/file_without_json_extension'
    selector: 'foo.0.bar'
    parser: 'json'
```

#### local_yaml_01
assign the env `local_yaml_01` from the JSON content using an xpath-style path selector to the desired value; js-style is also possible here.
```yaml
local_yaml_01:
    source: '/tmp/yamlfile.yaml'
    selector: 'foo.0.bar'
```

#### local_yaml_02
assign the env `local_yaml_02` from the YAML content using an xpath-style path selector to the desired value; set the YAML parser
```yaml
local_yaml_02:
    source: '/tmp/file_without_yaml_extension'
    selector: 'foo.0.bar'
    parser: 'yaml'
```

#### remote_text_01
Assign the env `remote_text_01` from the 1st line of the remote TEXT content
```yaml
remote_text_01:
    source: 'http://textfiles.com/computers/144disk.txt'
```

#### remote_json_01
Assign the env `remote_json_01` from remote JSON content using a jq-style selector
```yaml
remote_json_01:
    source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
    selector: '.prefixes[2].ip_prefix'
```

#### remote_json_02
Assign the env `remote_json_02` from remote JSON content using an xpath-style selector
```yaml
remote_json_02:
    source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
    selector: 'prefixes.2.ip_prefix'
```

#### exec_01
Assign the env `exec_01` from the 1st line of the STDOUT of an shell command
```yaml
exec_01:
    exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
```

#### exec_02
Assign the env `exec_02` from the 1st line of the STDOUT of an shell command
```yaml
exec_02:
    exec: 'curl -s https://ip-ranges.amazonaws.com/ip-ranges.json'
    parser: 'json'
    selector: '.prefixes[1].ip_prefix'
```  

#### exec_03
Run the shell-command and do not assign it to any env value
```yaml
exec_03:
    exec: 'head /dev/urandom | base64 -w0'
    selector: 'null'
```

#### direct_01
Assign env `direct_01` to value "somevalue"
```yaml
direct_01:
    value: 'somevalue'
```

#### direct_02
Use an existing env value as input into this configuration; can be used in any env-alias option
```yaml
direct_02:
    value: 'env:HOME'
```

#### direct_03
Set env set and override the variable name; can be used in any env-alias setting arrangement
```yaml
direct_03:
    name: 'direct_03_override_name'
    value: 'env:HOME'
```

## Debug Output
Debug output can be easily added to STDERR by adding an optional `-d` argument to `env-alias` as shown below

```bash
eval $(env-alias my-alias-name -d ~/path-to/my-alias-name-config-file.yml)
```

This this provides debug output similar to below

```text
username@computer:~$ my-alias-name
20191201Z072045 - DEBUG - env-alias v0.0.1
20191201Z072045 - DEBUG -  export "local_text_01"="xxxxxxxxxxxxxxxx"
20191201Z072045 - DEBUG -  export "local_text_02"="xxxxxxxxxxxxxxxx"
...
```


****

## Authors
[Nicholas de Jong](https://nicholasdejong.com)

## License
BSD-2-Clause - see LICENSE file for full details.

