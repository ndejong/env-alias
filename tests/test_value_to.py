import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def test_value_to_stderr_01(capsys, config_file):
    sentinal = "XXXX_foobar01_XXXX"
    yaml = f"""
        EXAMPLE:
            name: null
            value: "{sentinal}"
            value_to: "<stderr>"
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured_stderr = capsys.readouterr().err.rstrip()
    assert sentinal == captured_stderr

    captured_stdout = capsys.readouterr().out.rstrip()
    assert len(captured_stdout) == 0


def test_value_to_stderr_01_upper(capsys, config_file):
    sentinal = "XXXX_foobar01_XXXX"
    yaml = f"""
        EXAMPLE:
            name: null
            value: "{sentinal}"
            value_to: "<STDERR>"
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured_stderr = capsys.readouterr().err.rstrip()
    assert sentinal == captured_stderr

    captured_stdout = capsys.readouterr().out.rstrip()
    assert len(captured_stdout) == 0


def test_value_to_stdout_rejected(tmp_path, config_file):
    """value_to: <stdout> was removed (0.7.0); it must be rejected with guidance."""
    yaml = """
        EXAMPLE:
            name: null
            value: "x"
            value_to: "<stdout>"
    """

    f = config_file(yaml)
    with pytest.raises(EnvAliasException) as excinfo:
        EnvAliasGenerator(config_file=f).generate()

    message = str(excinfo.value)
    assert "removed" in message
    assert "<stderr>" in message


def test_value_to_stdout_upper_rejected(tmp_path, config_file):
    """Uppercase <STDOUT> is lowercased by the model and also rejected."""
    yaml = """
        EXAMPLE:
            name: null
            value: "x"
            value_to: "<STDOUT>"
    """

    f = config_file(yaml)
    with pytest.raises(EnvAliasException) as excinfo:
        EnvAliasGenerator(config_file=f).generate()

    assert "removed" in str(excinfo.value)


def test_value_to_buffering_on_failure(capsys, config_file):
    """
    Verifies P0-5: export lines are buffered so that if a later definition
    fails, nothing is written to stdout.
    """
    sentinal = "LEAKED"
    yaml = f"""
        ECHOED:
            value: "{sentinal}"
        BAD:
            source: "/nonexistent/nope.txt"
            selector: 1
    """

    f = config_file(yaml)

    # We expect it to raise EnvAliasException because of the BAD definition
    with pytest.raises(EnvAliasException):
        EnvAliasGenerator(config_file=f).generate()

    # Even though ECHOED resolved before BAD failed, NOTHING should be on
    # stdout because exports are buffered until every definition succeeds.
    captured_stdout = capsys.readouterr().out.rstrip()
    assert len(captured_stdout) == 0
