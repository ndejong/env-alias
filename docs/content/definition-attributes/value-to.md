# value_to

The `value_to` definition-attribute makes it possible to send the generated `value` to either STDOUT or STDERR.

This can be helpful in circumstances when a quick debug reveal is required or you need to provide some kind of 
user response.


### Example - to STDERR

```yaml
env-alias:
  
  EXAMPLE_STDERR:
    name: null
    value: "This is a message that will get sent to STDERR"
    value_to: "<STDERR>"
```


### Example - to STDOUT

```yaml
env-alias:
  
  EXAMPLE_STDOUT_CONTENT:
    name: null
    exec: "date"
  
  EXAMPLE_STDOUT:
    name: null
    exec: 'echo "The date is ${EXAMPLE_STDOUT_CONTENT} - boom!"'
    value_to: "<STDOUT>"
```
