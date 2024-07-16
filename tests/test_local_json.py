import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_yaml_01(capsys):
    test_file = os.path.join(
        tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)) + ".json"
    )
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_01:
        source: '{test_file}'
        selector: 'foo.1.bar'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_json_01"="value02"'


def test_sample_local_yaml_02(capsys):
    test_file = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_02:
        source: '{test_file}'
        selector: '.foo[1].bar'
        parser: 'json'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_json_02"="value02"'


def test_sample_local_yaml_03(capsys):
    test_file = (
        os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8))) + ".json"
    )
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_03:
        source: '{test_file}'
        selector: '.foo[3].bar.1'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_json_03"="value04.1"'


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)


def __write_json_test_file(filename) -> Path:
    config = """
    {
        "foo": [
            {"bar": "value01"},
            {"bar": "value02"},
            {"bar": "value03"},
            {"bar": ["value04.0","value04.1","value04.2"]}
        ]
    }
    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
