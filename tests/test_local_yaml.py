import os
import random
import string
import tempfile
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_yaml_01(capsys):
    test_file = os.path.join(
        tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)) + ".yml"
    )
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_01:
        source: '{test_file}'
        selector: 'foo.1.bar'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_yaml_01"="value02"'


def test_sample_local_yaml_02(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_02:
        source: '{test_file}'
        selector: 'zippy.catdog'
        parser: 'yaml'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_yaml_02"="12345"'


def test_sample_local_yaml_03_not_exist(capsys):
    test_file = (
        os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8))) + ".yml"
    )
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_03:
        source: '{test_file}'
        selector: '.foo[1].notexist'
    """

    config_file = __generate_config_file(yaml)

    with pytest.raises(EnvAliasException) as e_data:
        EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    assert "Unable to find data at supplied path in YAML content" in str(e_data)


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)


def __write_yaml_test_file(filename) -> Path:
    config = """
    foo:
        - bar: value01
        - bar: value02
        - bar: value03
        - bar: value04
    zippy:
        catdog: 12345
    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
