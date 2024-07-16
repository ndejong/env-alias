# parser

The parser defines the deserializer used to parse the source-content.

If the parser is not explicitly defined, EnvAlias will estimate what to use based on filename
extension or the http-remote `Content-Type` response header.

All other source-content is treated as plain text.


### Example - ini
Parse the `aws_access_key_id` from a standard AWS credentials file.
```yaml
env-alias:
  AWS_ACCESS_KEY_ID:
    source: "~/.aws/credentials"
    parser: ini
    selector: "default.aws_access_key_id"
```


### Example - yaml
Parse a value from `/foo/bar/data` in the file `/tmp/foobar.data` using an explict `yaml` parser because the filename
extension does not indicate a `.yaml` file.
```yaml
env-alias:
  EXAMPLE:
    source: "/tmp/foobar.data"
    parser: yaml
    selector: "/foo/bar/data"
```


### Example - json
Parse a value from `/foo/bar/data` in the file `/tmp/foobar.json` using an inferred `JSON` parser because the filename
infers the json file type. 
```yaml
env-alias:
  EXAMPLE:
    source: "/tmp/foobar.json"
    selector: "/foo/bar/data"
```


### Example - text
Read the source as text even though the filename indicates `.json` content type.
```yaml
env-alias:
  EXAMPLE:
    source: "/tmp/foobar.json"
    parser: text
    selector: 1
```
