
# AWS Credentials

An easy example to get AWS credentials loaded in as environment variables from a non-default AWS 
credentials file location.

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
