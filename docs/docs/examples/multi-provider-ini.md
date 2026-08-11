# Multi Provider INI Files

Load credentials for several cloud providers from existing INI account files in one invocation,
including Terraform-style `TF_VAR_*` names, without embedding any secret in the definition file.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}
[value](../definition-attributes/value.md){: .feat .f-value}

```yaml
env-alias:

  AWS_ACCESS_KEY_ID:
    source: "~/.credentials/aws/credentials"
    parser: "ini"
    selector: "workload.aws_access_key_id"

  AWS_SECRET_ACCESS_KEY:
    source: "~/.credentials/aws/credentials"
    parser: "ini"
    selector: "workload.aws_secret_access_key"

  AWS_DEFAULT_REGION:
    source: "~/.credentials/aws/config"
    parser: "ini"
    selector: "profile workload.region"

  TF_VAR_aws_access_key_id:
    value: "env:AWS_ACCESS_KEY_ID"

  ARM_SUBSCRIPTION_ID:
    source: "~/.credentials/azure/service-principal.ini"
    parser: "ini"
    selector: "service-principal.subscription_id"

  ARM_TENANT_ID:
    source: "~/.credentials/azure/service-principal.ini"
    parser: "ini"
    selector: "service-principal.tenant_id"

  ARM_CLIENT_ID:
    source: "~/.credentials/azure/service-principal.ini"
    parser: "ini"
    selector: "service-principal.client_id"

  ARM_CLIENT_SECRET:
    source: "~/.credentials/azure/service-principal.ini"
    parser: "ini"
    selector: "service-principal.client_secret"
```

Walkthrough:

1. `AWS_*` and `ARM_*` values are selected straight from their provider INI account files with
   `parser: ini`. The existing `credentials`/`config` directory layout is reused unchanged.
2. `TF_VAR_aws_access_key_id` aliases the resolved AWS key so Terraform picks it up as an input
   variable, without duplicating the secret.
3. Replace `workload`, `service-principal`, and the paths with your own account names. No secret
   appears in this file; it is all read from the local account files at load time.
