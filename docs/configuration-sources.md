# Env Alias

## Sources
All Env Alias definitions must have a `source`, `exec` or `value` that sets the source content that 
is subsequently passed to a parser.

Four types of sources are available:-
 * **source** (local) - any local file.
 * **source** (remote) - any http-remote object available via a GET request. 
 * **exec** (stdout) - the STDOUT content from a shell-exec command.
 * **value** (direct setting) - direct assignment of the value.

It is additionally possible to assign the `source`, `exec` or `value` setting through an environment 
variable itself by prefixing with `env:` this slightly unusual arrangement is useful when a source 
needs to be set with content that should not appear in the Env Alias configuration itself.

### Configuration Keyword Samples

```yaml
    source: "/etc/ssl/openssl.cnf"
```
Full pathname to config

```yaml
    source: "~/.aws/credentials"
```
Home-dir path to config

```yaml
    source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
```
Remote via http to config

```yaml
    source: "env:other_environment_variable"
```
Source location set by the value of the `other_environment_variable` environment variable. 

```yaml
    exec: "mkdir -p ~/.terraform.d/plugin-cache"
```
Exec a shell-command to mkdir, the empty response would be ignored

```yaml
    exec: "head /dev/urandom | base64 - -w0 | tr -d "=/+" | head -c20"
```
Exec a shell-command to generate a 20 character random value

```yaml
    exec: "ifconfig | grep 'inet ' | head -n1 | xargs | cut -d' ' -f2"
```
Exec a shell-command to extract the first ip4-address returned by ifconfig  

```yaml
    value: "foo"
```
Directly set the content value to "foo"
