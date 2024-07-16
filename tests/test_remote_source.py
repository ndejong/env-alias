import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_sample_remote_text_01(capsys):
    yaml = """
    sample_remote_text_01:
        source: 'http://textfiles.com/computers/144disk.txt'
        selector: 1
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_text_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_01(capsys):
    yaml = """
    sample_remote_json_01:
        source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        selector: '.prefixes[2].ip_prefix'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_json_01"=' in captured
    assert len(captured) >= 40


def test_sample_remote_json_02(capsys):
    yaml = """
    sample_remote_json_01:
        source: 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        selector: 'prefixes.2.ip_prefix'
    """

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "sample_remote_json_01"=' in captured
    assert len(captured) >= 40


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
