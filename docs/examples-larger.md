# Env Alias

## Larger examples
The following larger examples show what can be achieved when putting sets of Env Alias
configurations together.

### Ansible project setup
```yaml
env-alias:

    ANSIBLE_VAULT_PASSWORD:
        source: '~/secure/ansible-project/vault-pass.txt'

    ANSIBLE_VAULT_PASSWORD_FILE:
        value: '/tmp/.vault_echo_password'

    ANSIBLE_VAULT_PASSWORD_ECHO_FILE:
        exec: 'echo "#!/bin/sh" > /tmp/.vault_echo_password; echo "echo \${ANSIBLE_VAULT_PASSWORD}" >> /tmp/.vault_echo_password; chmod 700 /tmp/.vault_echo_password'
        selector: null

    ANSIBLE_SSH_PIPELINING:
        value: '1'

    ANSIBLE_SSH_KEYGEN:
        exec: 'rm -f ~/secure/tmp/init-deployment.key; ssh-keygen -N "" -f ~/secure/tmp/init-deployment.key 2>&1'
        selector: null

    ANSIBLE_SSH_ADD:
        exec: 'ssh-add -q ~/secure/tmp/init-deployment.key 2>&1'
        selector: null
```

### AWS project setup
```yaml
env-alias:

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

### Terraform - GCP project setup
```yaml
env-alias:

    CLOUDSDK_PYTHON:
        value: 'python3'

    TF_VAR_gcloud_keyfile_json:
        source: '~/secure/gcloud-account/service-account-1234567890.json'

    TF_VAR_gcloud_impersonated_user_email:
        value: 'admin@foobar.com'
```

### Terraform - AWS project setup
```yaml
env-alias:

    TF_PLUGIN_CACHE_DIR_CREATE:
        exec: 'mkdir -p ~/.terraform.d/plugin-cache'
        selector: null

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