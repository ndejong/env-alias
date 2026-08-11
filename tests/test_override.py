from env_alias.lib.generator import EnvAliasGenerator


def test_override_01(capsys, config_file):
    yaml = """
    test_override_01:
        value: "value01"

    test_override_02a:
        name: test_override_02
        value: "value02"

    test_override_02b:
        name: test_override_02
        value: "other02value"
        override: false
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert " export \"test_override_01\"='value01'" in captured
    assert " export \"test_override_02\"='value02'" in captured
    assert " export \"test_override_02\"='other02value'" not in captured
    assert len(captured) >= 30
