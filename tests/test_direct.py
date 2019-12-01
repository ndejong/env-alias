
import os
import tempfile
import random, string
import pytest
from unittest.mock import patch
import EnvAlias


def test_sample_direct_01(capsys):

    yaml = '''
    sample_direct_01:
        value: 'somevalue'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_01"="somevalue"'


def test_sample_direct_02(capsys):

    yaml = '''
    sample_direct_02:
        value: 'env:HOME'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_02"="{}"'.format(os.getenv('HOME'))


def test_sample_direct_03(capsys):

    yaml = '''
    sample_direct_03:
        name: 'sample_direct_03_override_name'
        value: 'env:HOME'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_direct_03_override_name"="{}"'.format(os.getenv('HOME'))


def __generate_config_file(yaml_config):
    config = 'env-alias:' + yaml_config
    filename = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, 'w') as f:
        f.write(config)
    return filename
