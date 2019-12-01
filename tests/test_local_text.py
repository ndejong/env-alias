
import os
import tempfile
import random, string
import pytest
from unittest.mock import patch
import EnvAlias


def test_sample_local_text_01(capsys):

    test_file = os.path.join(
        tempfile.gettempdir(),
        ''.join(random.choice(string.ascii_lowercase) for i in range(8)) + '.txt'
    )
    __write_text_test_file(test_file)

    yaml = '''
    sample_local_text_01:
        source: '{}'
    '''.format(test_file)

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_text_01"="value01"'


def test_sample_local_text_02(capsys):

    test_file = os.path.join(
        tempfile.gettempdir(),
        ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    )
    __write_text_test_file(test_file)

    yaml = '''
    sample_local_text_02:
        source: '{}'
        selector: '2'
    '''.format(test_file)

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)
    os.unlink(test_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "sample_local_text_02"="value02"'


def __generate_config_file(yaml_config):
    config = 'env-alias:' + yaml_config
    filename = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, 'w') as f:
        f.write(config)
    return filename


def __write_text_test_file(filename):
    config = '''value01
value02
value03
value04
    '''
    with open(filename, 'w') as f:
        f.write(config)
    return filename
