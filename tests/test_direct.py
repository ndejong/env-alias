import os

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_direct_01(capsys, config_file):
    yaml = """
    sample_direct_01:
        value: 'somevalue'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_direct_01\"='somevalue'"


def test_sample_direct_02(capsys, config_file):
    yaml = """
    sample_direct_02:
        value: 'env:HOME'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_direct_02\"='{}'".format(os.getenv("HOME"))


def test_sample_direct_03(capsys, config_file):
    yaml = """
    sample_direct_03:
        name: 'sample_direct_03_override_name'
        value: 'env:HOME'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_direct_03_override_name\"='{}'".format(os.getenv("HOME"))
