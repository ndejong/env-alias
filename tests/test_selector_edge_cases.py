import os

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator
from env_alias.lib.selector import EnvAliasSelector
from env_alias.models.envalias_definition import EnvAliasDefinition


def test_selector_zero_returns_last_line():
    """P1-4.1: selector: 0 should not return the last line."""
    content = "line1\nline2\nline3"
    # Current behavior: 0 - 1 = -1 -> lines[-1] -> "line3"
    # Expected behavior: raise EnvAliasException
    with pytest.raises(EnvAliasException):
        EnvAliasSelector.text_content(content, 0)


def test_selector_out_of_range_raises():
    """P1-4.2: selector one past the last line must raise."""
    # If content = "line1\nline2\nline3\n", lines = ["line1", "line2", "line3", ""]
    # len(lines) = 4. selector 4 returns lines[3] = ""
    content_with_newline = "line1\nline2\nline3\n"
    with pytest.raises(EnvAliasException):
        EnvAliasSelector.text_content(content_with_newline, 4)


def test_non_scalar_selection_rejected():
    """P1-4.3: non-scalar selections must be rejected."""
    content = '{"a": {"b": 1, "c": [1,2]}}'
    # Current behavior: selector "a" returns the dict {"b": 1, "c": [1,2]}
    # Expected behavior: raise EnvAliasException or similar
    with pytest.raises(EnvAliasException):
        EnvAliasSelector.json_content(content, "a")


def test_empty_value_supported():
    """P1-4.4: value: "" must be supported by the model."""
    # This test should fail if the model validator uses 'if not self.value'
    # We expect the model to be valid with an empty string.
    try:
        EnvAliasDefinition(name="TEST", value="")  # pyright: ignore[reportCallIssue]
    except Exception as e:
        pytest.fail(f"EnvAliasDefinition failed with empty value: {e}")


def test_override_false_respects_empty_value(capsys, config_file):
    """P1-4.5: override: false must respect an existing empty value."""
    # Setup: set an env var to empty string
    os.environ["EMPTY_VAR"] = ""
    try:
        yaml = """
            EMPTY_VAR:
                value: "new-value"
                override: false
        """
        f = config_file(yaml)
        EnvAliasGenerator(config_file=f).generate()

        captured_stdout = capsys.readouterr().out.rstrip()
        # If it respects empty value, it should NOT export "new-value"
        assert "EMPTY_VAR" not in captured_stdout
    finally:
        if "EMPTY_VAR" in os.environ:
            del os.environ["EMPTY_VAR"]
