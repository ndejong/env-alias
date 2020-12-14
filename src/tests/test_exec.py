
import os
from env_alias.EnvAliasGenerator import EnvAliasGenerator


def test_sample_exec_01(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'exec_01.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "exec_01"=' in captured
    assert len(captured) >= 20


def test_sample_exec_02(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'exec_02.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "exec_02"=' in captured
    assert len(captured) >= 20


def test_sample_exec_03(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'exec_03.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "exec_03"=' not in captured
    assert len(captured) == 0


def test_sample_exec_04(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'exec_04.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert ' export "exec_04"=' not in captured
    assert len(captured) == 0
