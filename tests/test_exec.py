
import os
import tempfile
import random, string
import pytest
from unittest.mock import patch
import EnvAlias


def test_sample_exec_01(capsys):

    yaml = '''
    sample_exec_01:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_01"=' in captured
    assert len(captured) >= 40


def test_sample_exec_02(capsys):

    yaml = '''
    sample_exec_02:
        exec: 'curl -s https://ip-ranges.amazonaws.com/ip-ranges.json'
        parser: 'json'
        selector: '.prefixes[1].ip_prefix'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_02"=' in captured
    assert len(captured) >= 40


def test_sample_exec_03(capsys):

    yaml = '''
    sample_exec_03:
        exec: 'head /dev/urandom | base64 -w0 | tr -d "/" | tr -d "+" | head -c20'
        selector: null
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_exec_03"=' not in captured
    assert len(captured) == 0


def __generate_config_file(yaml_config):
    config = 'env-alias:' + yaml_config
    filename = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, 'w') as f:
        f.write(config)
    return filename
