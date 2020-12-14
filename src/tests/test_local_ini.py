
import os
from env_alias.EnvAliasGenerator import EnvAliasGenerator
from . import __rewrite_configuration_file


def test_sample_local_ini_01(capsys):

    local_test_filename = os.path.join(os.path.dirname(__file__), 'samples', 'local.ini')
    temp_configuration_file = __rewrite_configuration_file(
        os.path.join(os.path.dirname(__file__), 'configs', 'local_ini_01.yml'),
        source=local_test_filename
    )

    EnvAliasGenerator().main(configuration_file=temp_configuration_file)
    os.unlink(temp_configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "local_ini_01"="value12345"'


def test_sample_local_ini_02(capsys):

    local_test_filename = os.path.join(os.path.dirname(__file__), 'samples', 'local.ini')
    temp_configuration_file = __rewrite_configuration_file(
        os.path.join(os.path.dirname(__file__), 'configs', 'local_ini_02.yml'),
        source=local_test_filename
    )

    EnvAliasGenerator().main(configuration_file=temp_configuration_file)
    os.unlink(temp_configuration_file)

    captured = capsys.readouterr().out.rstrip()
    assert captured == ' export "local_ini_02"="value12345"'


