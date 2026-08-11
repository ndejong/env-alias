from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_text_01(capsys, config_file, tmp_path):
    test_file = tmp_path / "test1.txt"
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_01:
        source: '{test_file}'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_text_01\"='value01'"


def test_sample_local_text_02(capsys, config_file, tmp_path):
    test_file = tmp_path / "test2.txt"
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_02:
        source: '{test_file}'
        selector: '2'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_text_02\"='value02'"


def test_sample_local_text_03_too_large(capsys, config_file, tmp_path):
    test_file = tmp_path / "test3.txt"
    __write_text_test_file(test_file)

    yaml = f"""
    sample_local_text_03:
        source: '{test_file}'
        selector: '99'
    """

    f = config_file(yaml)

    with pytest.raises(EnvAliasException) as e_data:
        EnvAliasGenerator(config_file=f).generate()

    assert "Text content selector 99 is out of range;" in str(e_data)


def __write_text_test_file(filename) -> Path:
    config = """value01
value02
value03
value04
    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
