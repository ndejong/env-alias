# exec

The `exec` definition-attribute can be used to obtain values from STDOUT when executing a shell command.   All the 
usual parsers and selectors are available as they are with other source types.

!!! warning
    
    It should be obvious, however, shell execution hazards and their appropriate precautions apply with this functionality.



### Example - curl

For example using `exec` it is possible to set external values by calling curl

```yaml
env-alias:
    EXAMPLE:
        exec: "curl -s https://ip-ranges.amazonaws.com/ip-ranges.json"
        parser: "json"
        selector: ".prefixes[1].ip_prefix"
```

This example is somewhat redundant because env-alias will perform a http-get request for any source definition
that looks like a URL anyway.


### Example - mkdir

This functionality can be useful in other ways too, such as making sure resources exist before loading an 
environment, for example create a path and skip setting the env variable.

```yaml
env-alias:
    EXAMPLE:
        name: null
        exec: "mkdir -p ~/.terraform.d/plugin-cache"
```


### Example - random string

Another example that invokes a shell-command to generate a 20 character random value, by default the 
source-type is `text` and the selector will take the first line so no further definition is required here. 

```yaml
env-alias:
    EXAMPLE:
        exec: "head /dev/urandom | base64 - -w0 | tr -d "=/+" | head -c20"
```


If we expand this into long-form with its parser and selector, we'd get the same thing.
```yaml
env-alias:
    EXAMPLE:
        exec: "head /dev/urandom | base64 - -w0 | tr -d "=/+" | head -c20"
        parser: "text"
        selector: 1
```

### Example - host ip addr

Another example to obtain the first ip-address on the first interface of the host  

```yaml
env-alias:
    EXAMPLE:
        exec: "ip -json addr | jq -r .[1].addr_info[0].local"
```
