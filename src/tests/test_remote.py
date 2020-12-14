
import os
from env_alias.EnvAliasGenerator import EnvAliasGenerator


def test_sample_remote_text_01(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'remote_text_01.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "remote_text_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_01(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'remote_json_01.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "remote_json_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_02(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'remote_json_02.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "remote_json_02"=' in captured
    assert len(captured) >= 40
