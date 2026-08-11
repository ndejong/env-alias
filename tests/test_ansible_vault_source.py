import shutil

import pytest

from env_alias.lib.generator import EnvAliasGenerator

pytestmark = [
    pytest.mark.requires_ansible_vault,
    pytest.mark.skipif(
        shutil.which("ansible-vault") is None,
        reason="ansible-vault not found on PATH",
    ),
]


def test_ansiblevault_01(capsys, config_file):
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

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert " export \"test_value_username\"='foo'" in captured
    assert " export \"test_value_password\"='bar'" in captured
