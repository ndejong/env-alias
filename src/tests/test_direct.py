
import os
from env_alias.EnvAliasGenerator import EnvAliasGenerator


def test_sample_direct_01(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'direct_01.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "direct_01"="somevalue"'


def test_sample_direct_02(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'direct_02.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "direct_02"="{}"'.format(os.getenv('HOME'))


def test_sample_direct_03(capsys):
    configuration_file = os.path.join(os.path.dirname(__file__), 'configs', 'direct_03.yml')
    EnvAliasGenerator().main(configuration_file=configuration_file)
    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "direct_03_override_name"="{}"'.format(os.getenv('HOME'))
