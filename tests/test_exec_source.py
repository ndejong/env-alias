import random
import string

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_sample_exec_01(capsys, config_file):
    yaml = """
    sample_exec_01:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_01"=' in captured
    assert len(captured) >= 40


def test_sample_exec_02(http_file_server, capsys, config_file):
    yaml = f"""
    sample_exec_02:
        exec: 'curl -s {http_file_server}/data.json'
        parser: 'json'
        selector: '.prefixes[1].ip_prefix'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_02"=' in captured
    assert "1.1.1.1/32" in captured


def test_sample_exec_03(capsys, config_file):
    yaml = """
    sample_exec_03:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
        selector: null
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_03"=' not in captured
    assert len(captured) == 0


def test_sample_exec_04_legacy_none(capsys, config_file):
    yaml = """
    sample_exec_04:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
        selector: none
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_04"=' not in captured
    assert len(captured) == 0


def test_sample_bad_exec_01(capsys, config_file):
    yaml = """
    sample_exec_bad_01:
        exec: 'unknown-command-JHKJKHGJKHG'
    """

    f = config_file(yaml)

    with pytest.raises(EnvAliasException) as e_info:
        EnvAliasGenerator(config_file=f).generate()

    assert "unknown-command-JHKJKHGJKHG: not found" in str(e_info)


def test_sample_exec_env_to_exec_01(capsys, config_file):
    test_value = "".join(random.choice(string.ascii_lowercase) for _ in range(8))

    yaml = f"""
        env_to_exec_step01:
            name: RANDOM_VALUE
            value: '{test_value}'
        TEST_VALUE:
            exec: >
                echo "> ${{RANDOM_VALUE}} <"
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert f" export \"TEST_VALUE\"='> {test_value} <'" in captured
