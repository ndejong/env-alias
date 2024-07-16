import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_keepass_01(capsys):
    yaml = """
    password_for_keepass_database:
        name: null
        source: "tests/data/envalias-keepass-database-password.txt"
        selector: 7

    test_value_username:
        source: "tests/data/envalias-keepass-database.kdbx"
        keepass_password: "env:password_for_keepass_database"
        selector: "group02/subgroup02b/envalias-test02:Username"

    test_value_password:
        source: "tests/data/envalias-keepass-database.kdbx"
        keepass_password: "env:password_for_keepass_database"
        selector: "group02/subgroup02b/envalias-test02:Password"
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert "username-test02" in captured
    assert "password-test02-beep" in captured


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
