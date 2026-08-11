from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_local_yaml_01(capsys, config_file, tmp_path):
    test_file = tmp_path / "test1.json"
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_01:
        source: '{test_file}'
        selector: 'foo.1.bar'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_json_01\"='value02'"


def test_sample_local_yaml_02(capsys, config_file, tmp_path):
    test_file = tmp_path / "test2.json"
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_02:
        source: '{test_file}'
        selector: '.foo[1].bar'
        parser: 'json'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_json_02\"='value02'"


def test_sample_local_yaml_03(capsys, config_file, tmp_path):
    test_file = tmp_path / "test3.json"
    __write_json_test_file(test_file)

    yaml = f"""
    sample_local_json_03:
        source: '{test_file}'
        selector: '.foo[3].bar.1'
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert captured == " export \"sample_local_json_03\"='value04.1'"


def __write_json_test_file(filename) -> Path:
    config = """
    {
        "foo": [
            {"bar": "value01"},
            {"bar": "value02"},
            {"bar": "value03"},
            {"bar": ["value04.0","value04.1","value04.2"]}
        ]
    }
    """
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
