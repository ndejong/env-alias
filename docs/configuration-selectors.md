# Env Alias

## Selectors
Selectors make it possible to "pick" a value from the parsed content.  

Structured content formats (ini, yaml, json) support dot-notation (eg: `foo.0.bar`) and 
brace-notation (eg: `foo[0]bar`) as data selectors.

Text files support line-number selectors only.

A special `none` (also `null`) selector exists which prevents any environment variable setting 
which is useful when using a shell-exec and the output is not needed.

### Configuration Keyword Samples
```yaml
    selector: '.prefixes[1].ip_prefix'
```
Select from a structured data file the second `ip_prefix`  

```yaml
    selector: none
```
Do not assign the selector response data to an environment variable.

```yaml
    selector: 2
```
Select the second line as might be done when working with text files.
