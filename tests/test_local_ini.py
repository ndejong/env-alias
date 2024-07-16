import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_ini_01(capsys):
    test_file = os.path.join(
        tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)) + ".ini"
    )
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_01:
        source: '{test_file}'
        selector: 'foo.bar'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_ini_01"="value12345"'


def test_sample_local_ini_02(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_02:
        source: '{test_file}'
        selector: 'foo.bar'
        parser: 'ini'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_ini_02"="value12345"'


def test_sample_local_ini_03(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_03:
        source: '{test_file}'
        selector: 'cat.bar'
        parser: 'ini'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_ini_03"="some_value_67890"'


def test_sample_local_ini_04(capsys):
    test_file = (
        os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8))) + ".ini"
    )
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_04a:
        source: '{test_file}'
        selector: 'foo.other'
        name: 'awesome01'

    sample_local_ini_04b:
        source: '{test_file}'
        selector: 'cat.bar'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "awesome01"="some_value_12345"' in captured
    assert ' export "sample_local_ini_04b"="some_value_67890"' in captured


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)


def __write_ini_test_file(filename) -> Path:
    config = """

[foo]
bar = value12345
other = some_value_12345

[cat]
bar = some_value_67890

    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
