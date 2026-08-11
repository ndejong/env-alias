from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_ini_01(capsys, config_file, tmp_path):
    test_file = tmp_path / "test1.ini"
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_01:
        source: '{test_file}'
        selector: 'foo.bar'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_ini_01\"='value12345'"


def test_sample_local_ini_02(capsys, config_file, tmp_path):
    test_file = tmp_path / "test2.ini"
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_02:
        source: '{test_file}'
        selector: 'foo.bar'
        parser: 'ini'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_ini_02\"='value12345'"


def test_sample_local_ini_03(capsys, config_file, tmp_path):
    test_file = tmp_path / "test3.ini"
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_03:
        source: '{test_file}'
        selector: 'cat.bar'
        parser: 'ini'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_ini_03\"='some_value_67890'"


def test_sample_local_ini_04(capsys, config_file, tmp_path):
    test_file = tmp_path / "test4.ini"
    __write_ini_test_file(test_file)

    yaml = f"""
    sample_local_ini_04a:
        source: '{test_file}'
        selector: 'foo.other'
        name: 'awesome01'

    sample_local_ini_04b:
        source: '{test_file}'
        selector: 'cat.bar'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert " export \"awesome01\"='some_value_12345'" in captured
    assert " export \"sample_local_ini_04b\"='some_value_67890'" in captured


def __write_ini_test_file(filename) -> Path:
    config = """

[foo]
bar = value12345
other = some_value_12345

[cat]
bar = some_value_67890

    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
