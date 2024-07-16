import os
import random
import string
import tempfile
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_text_01(capsys):
    test_file = os.path.join(
        tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)) + ".txt"
    )
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_01:
        source: '{test_file}'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_text_01"="value01"'


def test_sample_local_text_02(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_02:
        source: '{test_file}'
        selector: '2'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_text_02"="value02"'


def test_sample_local_text_03_too_large(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_03:
        source: '{test_file}'
        selector: '99'
    """

    config_file = __generate_config_file(yaml)

    with pytest.raises(EnvAliasException) as e_data:
        EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    assert "Text content selector 99 is out of range;" in str(e_data)


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)


def __write_text_test_file(filename) -> Path:
    config = """value01
value02
value03
value04
    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
