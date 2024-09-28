# Terraform AWS project

## Example

The example below shows an Env Alias definition for setting up a Terraform environment.  Notice that 
all parts of the environment are easily established by calling a single alias name and that no secret
values are contained within.

 * Environment variable `TF_VAR_aws_access_key_id` is set by reading the file `~/.aws/credentials` 
   and selecting the value from `account_name.aws_access_key_id` 
 * Environment variable `TF_VAR_aws_secret_access_key` is set in a similar manner.
 * The path `~/.terraform.d/plugin-cache` is created and the shell exec stdout is discarded.
 * Environment variable `TF_PLUGIN_CACHE_DIR` is set directly in-line to the value `~/.terraform.d/plugin-cache`

```yaml
env-alias:

    TF_PLUGIN_CACHE_DIR_CREATE:
        name: null
        exec: 'mkdir -p ~/.terraform.d/plugin-cache'

    TF_PLUGIN_CACHE_DIR:
        value: '~/.terraform.d/plugin-cache'

    TF_VAR_aws_access_key_id:
        source: '~/.aws/credentials'
        parser: 'ini'
        selector: 'account_name.aws_access_key_id'

    TF_VAR_aws_secret_access_key:
        source: '~/.aws/credentials'
        parser: 'ini'
        selector: 'account_name.aws_secret_access_key'

    TF_VAR_aws_default_region:
        source: '~/.aws/config'
        parser: 'ini'
        selector: 'profile account_name.region'

    TF_VAR_aws_ssh_key_name:
        value: 'username'
```
