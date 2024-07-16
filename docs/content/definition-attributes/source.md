# source

All Env Alias definitions should have a `source`, `exec` or `value` that sets the source content that 
is subsequently passed to a parser.

Four types of sources are available -

 * **source** (local) - any local file.
 * **source** (remote) - any http-remote object available via a GET request. 
 * **exec** (stdout) - the STDOUT content from a shell-exec command.
 * **value** (direct setting) - direct assignment of the value.

It is possible to reference other environment-variables within a definition by using its name prefixed with 
an `env:` string.


### Example - simple
Source content from line 5 in source file `/proc/cpuinfo` and assign to env-variable `EXAMPLE`   
```yaml
env-alias:
  EXAMPLE:
    source: "/proc/cpuinfo"
    selector: 5
```


### Example - getpass
Source content from the user using Python [getpass](https://docs.python.org/3/library/getpass.html) that is part 
of the Python standard libraries.  The Python getpass module ensures input is not echoed to terminal
```yaml
env-alias:
  EXAMPLE:
    source: "<getpass>"
```


### Example - stdin

Source content from STDIN, that will be observable in the terminal output.
```yaml
env-alias:
  EXAMPLE:
    source: "<stdin>"
```


### Example - home path

Source content from a file in the user home-path using tilde (`~`) notation.
```yaml
env-alias:
  AWS_ACCESS_KEY_ID:
    source: "~/.aws/credentials"
    parser: ini
    selector: "profile_name.aws_access_key_id"
```


### Example - http remote

Source content from a remote HTTP source
```yaml
env-alias:
  EXAMPLE:
    source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
    selector: "prefixes.2.ip_prefix"
```


### Example - env reference

Source location set by the value of another environment variable `EXAMPLE_SOURCE`. 
```yaml
env-alias:
  EXAMPLE_SOURCE:
    value: "/proc/cpuinfo"
  EXAMPLE:
    source: "env:EXAMPLE_SOURCE"
    selector: 5
```
