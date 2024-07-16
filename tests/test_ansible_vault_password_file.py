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

    ANSIBLE_VAULT_PASSWORD_FILE:
        ansible_vault_password: "env:password_for_ansible_vault"
        ansible_vault_password_file: true
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert '"="envalias-ansible-test-only-password"' in captured
    assert '"ANSIBLE_VAULT_PASSWORD_FILE"="/tmp/' in captured


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
