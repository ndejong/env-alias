import os
import random
import string
import tempfile
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_exec_01(capsys):
    yaml = """
    sample_exec_01:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_01"=' in captured
    assert len(captured) >= 40


def test_sample_exec_02(capsys):
    yaml = """
    sample_exec_02:
        exec: 'curl -s https://ip-ranges.amazonaws.com/ip-ranges.json'
        parser: 'json'
        selector: '.prefixes[1].ip_prefix'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_02"=' in captured
    assert len(captured) >= 35  # ' export "sample_exec_02"="0.0.0.0/0"'


def test_sample_exec_03(capsys):
    yaml = """
    sample_exec_03:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
        selector: null
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_03"=' not in captured
    assert len(captured) == 0


def test_sample_exec_04_legacy_none(capsys):
    yaml = """
    sample_exec_04:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
        selector: none
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_04"=' not in captured
    assert len(captured) == 0


def test_sample_bad_exec_01(capsys):
    yaml = """
    sample_exec_bad_01:
        exec: 'unknown-command-JHKJKHGJKHG'
    """

    config_file = __generate_config_file(yaml)

    with pytest.raises(EnvAliasException) as e_info:
        EnvAliasGenerator(config_file=config_file).generate()

    assert "unknown-command-JHKJKHGJKHG: not found" in str(e_info)


def test_sample_exec_env_to_exec_01(capsys):
    test_value = "".join(random.choice(string.ascii_lowercase) for _ in range(8))

    yaml = """
        env_to_exec_step01:
            name: RANDOM_VALUE
            value: '{test_value}'
        TEST_VALUE:
            exec: >
                echo "> ${{RANDOM_VALUE}} <"
    """.format(
        test_value=test_value
    )

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert f' export "TEST_VALUE"="> {test_value} <"' in captured


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
