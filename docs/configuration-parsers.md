# Env Alias

## Parsers
If the parser is not defined, Env Alias will estimate the source content format based on filename
extension, either `.ini`, `.json`, `.yml` or `.yaml` otherwise the content will be treated as plain
text.

Additionally, source content retrieved using a http-remote source will attempt to use the `Content-Type` 
response header to estimate the content format, again if not otherwise configured.

### Configuration Keyword Samples

```yaml
    parser: 'yaml'
```
Use YAML content parsing

```yaml
    parser: 'json'
```
Use JSON content parsing

```yaml
    parser: 'ini'
```
Use ini/config content parsing

```yaml
    parser: 'text'
```
Use plain-text content parsing
