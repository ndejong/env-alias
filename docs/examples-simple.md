# Env Alias

## Simple examples
The following examples iterate through most of the possible permutations of source, parser
and selector. 

### local_text_01
```yaml
env-alias:
  local_text_01:
    source: "/tmp/textfile.txt"
```
Assign the env `local_text_01` to the value of the 1st line of text in `/tmp/textfile.txt`

### local_text_02
```yaml
env-alias:
  local_text_02:
    source: "/tmp/textfile.txt"
    selector: 2
```
Assign the env `local_text_02` to the value of the 2nd line of text in `/tmp/textfile.txt`

### local_text_03
```yaml
env-alias:
  local_text_03:
    source: "/tmp/textfile_without_extension"
```
Assign the env `local_text_03` using the 1st line of text in the text file; text file format used as default file format

### local_text_04
```yaml
env-alias:
  local_text_04:
    name: "local_text_04_override_name"
    source: "/tmp/textfile.txt"
```
Assign the env `local_text_04_override_name` using the 1st line of text in the file and use a different variable name

### local_text_05
```yaml
env-alias:
  local_text_05:
    source: "env:some_env_with_a_filename"
```
Assign the env `local_text_05` using the 1st line of text in the file specified by env variable `${some_env_with_a_filename}`

### local_text_06
```yaml
env-alias:
  local_text_06:
    source: "/tmp/textfile.txt"
    parser: "text"
```
Assign the env `local_text_06` using the 1st line of text in the file and force the "text" content parser which is the default parser anyway

### local_ini_01
```yaml
env-alias:
  local_ini_01:
    source: "/tmp/inifile.ini"
    selector: "foo.bar"
```
Assign the env `local_ini_01` from the `[foo]` section under the `[bar]` option value; parser determined by filename extension

### local_ini_02
```yaml
env-alias:
  local_ini_02:
    source: "/tmp/file_without_ini_extension"
    selector: "foo.bar"
    parser: "ini"
```
Assign the env `local_ini_02` from the `[foo]` section under the `[bar]` option value; parser manually set since it can not be determined via filename extension

### local_json_01
```yaml
env-alias:
  local_json_01:
    source: "/tmp/jsonfile.json"
    selector: "foo.0.bar"
```  
Assign the env `local_json_01` from the JSON content using an xpath-style path selector to the desired value

### local_json_02
```yaml
env-alias:
  local_json_02:
    source: "/tmp/jsonfile.json"
    selector: ".foo[1]bar"
```
Assign the env `local_json_02` from the JSON content using a jq-style path selector to the desired value

### local_json_03
```yaml
env-alias:
  local_json_03:
    source: "/tmp/file_without_json_extension"
    selector: "foo.0.bar"
    parser: "json"
```
Assign the env `local_json_03` from the JSON content using an xpath-style path selector to the desired value; set the JSON parser

### local_yaml_01
```yaml
env-alias:
  local_yaml_01:
    source: "/tmp/yamlfile.yml"
    selector: "foo.0.bar"
```
Assign the env `local_yaml_01` from the JSON content using an xpath-style path selector to the desired value; js-style is also possible here.

### local_yaml_02
```yaml
env-alias:
  local_yaml_02:
    source: "/tmp/file_without_yaml_extension"
    selector: "foo.0.bar"
    parser: "yaml"
```
Assign the env `local_yaml_02` from the YAML content using an xpath-style path selector to the desired value; set the YAML parser

### remote_text_01
```yaml
env-alias:
  remote_text_01:
    source: "http://textfiles.com/computers/144disk.txt"
```
Assign the env `remote_text_01` from the 1st line of the remote TEXT content

### remote_json_01
```yaml
env-alias:
  remote_json_01:
    source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
    selector: ".prefixes[2].ip_prefix"
```
Assign the env `remote_json_01` from remote JSON content using a jq-style selector

### remote_json_02
```yaml
env-alias:
  remote_json_02:
    source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
    selector: "prefixes.2.ip_prefix"
```
Assign the env `remote_json_02` from remote JSON content using an xpath-style selector

### exec_01
```yaml
env-alias:
  exec_01:
    exec: "head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20"
```
Assign the env `exec_01` from the 1st line of the STDOUT of an shell command

### exec_02
```yaml
env-alias:
  exec_02:
    exec: "curl -s https://ip-ranges.amazonaws.com/ip-ranges.json"
    parser: "json"
    selector: ".prefixes[1].ip_prefix"
```  
Assign the env `exec_02` from the 1st line of the STDOUT of an shell command

### exec_03
```yaml
env-alias:
  exec_03:
    exec: "head /dev/urandom | base64 -w0"
    selector: null
```
Run the shell-command and do not assign it to any env value

### direct_01
```yaml
env-alias:
  direct_01:
    value: "somevalue"
```
Assign env `direct_01` to value "somevalue"

### direct_02
```yaml
env-alias:
  direct_02:
    value: "env:HOME"
```
Use an existing env value as input into this configuration; can be used in any env-alias option

### direct_03
```yaml
env-alias:
  direct_03:
    name: "direct_03_override_name"
    value: "env:HOME"
```
Set env set and override the variable name; can be used in any env-alias setting arrangement
