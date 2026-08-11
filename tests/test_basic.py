import contextlib
import io
from pathlib import Path

import env_alias
from env_alias.lib.generator import EnvAliasGenerator


def test_name_exist():
    ea = env_alias
    assert ea.__title__ is not None


def test_version_exist():
    ea = env_alias
    assert ea.__version__ is not None


def test_value_empty_string(tmp_path: Path, config_file):
    """P1-4b: value: \"\" must export with empty value and exit 0."""
    config = config_file('    EMPTY:\n        value: ""\n')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        EnvAliasGenerator(config_file=config).generate()
    output = buf.getvalue()
    assert 'export "EMPTY"=' in output
    # empty string value should be single-quoted as ''
    assert "''" in output
