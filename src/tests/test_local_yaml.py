
import os
from env_alias.EnvAliasGenerator import EnvAliasGenerator
from . import __rewrite_configuration_file


def test_sample_local_yaml_01(capsys):

    local_test_filename = os.path.join(os.path.dirname(__file__), 'samples', 'local.yml')
    temp_configuration_file = __rewrite_configuration_file(
        os.path.join(os.path.dirname(__file__), 'configs', 'local_yaml_01.yml'),
        source=local_test_filename
    )

    EnvAliasGenerator().main(configuration_file=temp_configuration_file)
    os.unlink(temp_configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "local_yaml_01"="value02"'


def test_sample_local_yaml_02(capsys):

    local_test_filename = os.path.join(os.path.dirname(__file__), 'samples', 'local.yml')
    temp_configuration_file = __rewrite_configuration_file(
        os.path.join(os.path.dirname(__file__), 'configs', 'local_yaml_02.yml'),
        source=local_test_filename
    )

    EnvAliasGenerator().main(configuration_file=temp_configuration_file)
    os.unlink(temp_configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "local_yaml_02"="value03"'
