
import os
import tempfile
import random, string
import pytest
from unittest.mock import patch
import EnvAlias


def test_sample_remote_text_01(capsys):

    yaml = '''
    sample_remote_text_01:
        source: 'http://textfiles.com/computers/144disk.txt'
        selector: 1
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_text_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_01(capsys):

    yaml = '''
    sample_remote_json_01:
        source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        selector: '.prefixes[2].ip_prefix'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_json_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_02(capsys):

    yaml = '''
    sample_remote_json_01:
        source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        selector: 'prefixes.2.ip_prefix'
    '''

    configuration_file = __generate_config_file(yaml)
    EnvAlias.EnvAlias().main(configuration_file=configuration_file)
    os.unlink(configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_json_01"=' in captured
    assert len(captured) >= 40


def __generate_config_file(yaml_config):
    config = 'env-alias:' + yaml_config
    filename = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, 'w') as f:
        f.write(config)
    return filename
