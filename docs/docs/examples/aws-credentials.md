# AWS Credentials INI files

An easy example to get AWS credentials loaded in as environment variables from a non-default AWS
credentials file location.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}

```yaml
env-alias:

    AWS_ACCESS_KEY_ID:
        source: '~/credentials/aws/account_xxx/credentials'
        parser: 'ini'
        selector: 'profile_name.aws_access_key_id'

    AWS_SECRET_ACCESS_KEY:
        source: '~/credentials/aws/account_xxx/credentials'
        parser: 'ini'
        selector: 'profile_name.aws_secret_access_key'

    AWS_DEFAULT_REGION:
        source: '~/.aws/config'
        parser: 'ini'
        selector: 'profile account_name.region'
```

Walkthrough:

1. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are pulled from a non-default credentials file with
   `parser: ini`, selecting the `aws_access_key_id` / `aws_secret_access_key` fields of the
   `profile_name` section.
2. `AWS_DEFAULT_REGION` is read from the separate `~/.aws/config` file, using the
   `profile <name>.<field>` selector syntax.
