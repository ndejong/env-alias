
import os
import tempfile
import random, string
import pytest
from unittest.mock import patch
import EnvAlias


def test_sample_local_yaml_01(capsys):

    test_file = os.path.join(
        tempfile.gettempdir(),
        ''.join(random.choice(string.ascii_lowercase) for i in range(8)) + '.yml'
    )
    __write_yaml_test_file(test_file)

    yaml = '''
    sample_local_yaml_01:
        source: '{}'
        selector: 'foo.1.bar'
    '''.format(test_file)

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_yaml_01"="value02"'


def test_sample_local_yaml_02(capsys):

    test_file = os.path.join(
        tempfile.gettempdir(),
        ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    )
    __write_yaml_test_file(test_file)

    yaml = '''
    sample_local_yaml_02:
        source: '{}'
        selector: '.foo[1].bar'
        parser: 'yaml'
    '''.format(test_file)

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_yaml_02"="value02"'


def __generate_config_file(yaml_config):
    config = 'env-alias:' + yaml_config
    filename = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, 'w') as f:
        f.write(config)
    return filename


def __write_yaml_test_file(filename):
    config = '''
    foo:
        - bar: value01
        - bar: value02
        - bar: value03
        - bar: value04
    '''
    with open(filename, 'w') as f:
        f.write(config)
    return filename
