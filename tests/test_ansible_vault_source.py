import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_ansiblevault_01(capsys):
    yaml = """
    password_for_ansible_vault:
        name: null
        source: "tests/data/envalias-ansible-vault-datafile-password.txt"
        selector: 7

    test_value_username:
        source: "tests/data/envalias-ansible-vault-datafile.vault"
        ansible_vault_password: "env:password_for_ansible_vault"
        selector: "all/vars/vault/project_foobar/username"

    test_value_password:
        source: "tests/data/envalias-ansible-vault-datafile.vault"
        ansible_vault_password: "env:password_for_ansible_vault"
        selector: "all/vars/vault/project_foobar/password"
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "test_value_username"="foo"' in captured
    assert ' export "test_value_password"="bar"' in captured


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
