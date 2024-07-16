import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_direct_01(capsys):
    yaml = """
    sample_direct_01:
        value: 'somevalue'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_01"="somevalue"'


def test_sample_direct_02(capsys):
    yaml = """
    sample_direct_02:
        value: 'env:HOME'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_02"="{}"'.format(os.getenv("HOME"))


def test_sample_direct_03(capsys):
    yaml = """
    sample_direct_03:
        name: 'sample_direct_03_override_name'
        value: 'env:HOME'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_03_override_name"="{}"'.format(os.getenv("HOME"))


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
