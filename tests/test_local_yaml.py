from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_yaml_01(capsys, config_file, tmp_path):
    test_file = tmp_path / "test1.yml"
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_01:
        source: '{test_file}'
        selector: 'foo.1.bar'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_yaml_01\"='value02'"


def test_sample_local_yaml_02(capsys, config_file, tmp_path):
    test_file = tmp_path / "test2.yml"
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_02:
        source: '{test_file}'
        selector: 'zippy.catdog'
        parser: 'yaml'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_yaml_02\"='12345'"


def test_sample_local_yaml_03_not_exist(capsys, config_file, tmp_path):
    test_file = tmp_path / "test3.yml"
    __write_yaml_test_file(test_file)

    yaml = f"""
    sample_local_yaml_03:
        source: '{test_file}'
        selector: '.foo[1].notexist'
    """

    f = config_file(yaml)

    with pytest.raises(EnvAliasException) as e_data:
        EnvAliasGenerator(config_file=f).generate()

    assert "Unable to find data at supplied path in YAML content" in str(e_data)


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
