import os
import random
import string
import tempfile
from pathlib import Path

from env_alias.lib.generator import EnvAliasGenerator


def test_override_01(capsys):
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

    config_file = __generate_config_file(yaml)
    EnvAliasGenerator(config_file=config_file).generate()
    os.unlink(config_file)

    captured = capsys.readouterr().out.rstrip()
    assert ' export "test_override_01"="value01"' in captured
    assert ' export "test_override_02"="value02"' in captured
    assert ' export "test_override_02"="other02value"' not in captured
    assert len(captured) >= 40


def __generate_config_file(yaml_config) -> Path:
    config = "env-alias:" + yaml_config
    filename = os.path.join(tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for i in range(8)))
    with open(filename, "w") as f:
        f.write(config)
    return Path(filename)
