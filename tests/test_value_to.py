import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_value_to_stderr_01(capsys):
    sentinal = "XXXX_foobar01_XXXX"
    yaml = f"""
        EXAMPLE:
            name: null
            value: "{sentinal}"
            value_to: "<stderr>"
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured_stderr = capsys.readouterr().err.rstrip()
    assert sentinal == captured_stderr

    captured_stdout = capsys.readouterr().out.rstrip()
    assert len(captured_stdout) == 0


def test_value_to_stderr_01_upper(capsys):
    sentinal = "XXXX_foobar01_XXXX"
    yaml = f"""
        EXAMPLE:
            name: null
            value: "{sentinal}"
            value_to: "<STDERR>"
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured_stderr = capsys.readouterr().err.rstrip()
    assert sentinal == captured_stderr

    captured_stdout = capsys.readouterr().out.rstrip()
    assert len(captured_stdout) == 0


def test_value_to_stderr_02(capsys):
    sentinal = "XXXX_foobar02_XXXX"
    yaml = f"""
        EXAMPLE:
            name: null
            value: "{sentinal}"
            value_to: "<stdout>"
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured_stdout = capsys.readouterr().out.rstrip()
    assert sentinal == captured_stdout

    captured_stderr = capsys.readouterr().err.rstrip()
    assert len(captured_stderr) == 0


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
