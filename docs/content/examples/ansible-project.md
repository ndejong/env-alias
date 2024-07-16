
# Ansible Project

An example env-alias definition file for an Ansible project, this example does a few neat things -

 * Sets up the `ANSIBLE_VAULT_PASSWORD_FILE` without any additional setup
 * Sets the `ANSIBLE_SSH_PIPELINING` to reduce latency between Ansible calls, thus speeding things up.
 * Creates a throw-away SSH keypair that can be used to bootstrap a target instance 

```yaml
env-alias:
  
  MYPROJECT_ANSIBLE_VAULT_PASSWORD:
    name: null  # prevents this value being assigned into env
    source: '~/secure/ansible-project/vault-pass.txt'

  ANSIBLE_VAULT_PASSWORD_FILE:
    ansible_vault_password: "env:MYPROJECT_ANSIBLE_VAULT_PASSWORD"  # NB: see docs how this gets managed
    ansible_vault_password_file: true  # invoke special helper that renders an Ansible Vault password file
    
  ANSIBLE_SSH_PIPELINING:
    value: '1'

  MYPROJECT_BOOTSTRAP_SSH_KEYGEN:
    exec: 'rm -f ~/secure/tmp/init-deployment.key; ssh-keygen -N "" -f ~/secure/tmp/init-deployment.key 2>&1'
    name: null

  MYPROJECT_BOOTSTRAP_SSH_KEYADD:
    exec: 'ssh-add -q ~/secure/tmp/init-deployment.key 2>&1'
    name: null
```
