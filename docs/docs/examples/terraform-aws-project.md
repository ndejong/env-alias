# Terraform on AWS

Configure Terraform's plugin cache and the AWS provider's standard environment variables from local
AWS configuration files, without placing credentials in the definition file.

## Example

[exec](../definition-attributes/exec.md){: .feat .f-exec}
[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}

```yaml
env-alias:
  TF_PLUGIN_CACHE_DIR:
    exec: 'mkdir -p "$HOME/.terraform.d/plugin-cache" && printf "%s/.terraform.d/plugin-cache" "$HOME"'

  AWS_ACCESS_KEY_ID:
    source: '~/.aws/credentials'
    parser: 'ini'
    selector: 'account_name.aws_access_key_id'

  AWS_SECRET_ACCESS_KEY:
    source: '~/.aws/credentials'
    parser: 'ini'
    selector: 'account_name.aws_secret_access_key'

  AWS_DEFAULT_REGION:
    source: '~/.aws/config'
    parser: 'ini'
    selector: 'profile account_name.region'
```

Walkthrough:

1. `TF_PLUGIN_CACHE_DIR` creates the directory and prints its fully expanded path. `exec` uses that
   stdout value for the export, avoiding a literal unexpanded `~` path.
2. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` are the standard names read
   by the AWS provider. Each is selected from the relevant AWS INI file.
3. Replace `account_name` with an existing profile. This example configures provider credentials; a
   Terraform input variable would require a matching `variable` declaration in your Terraform code.
