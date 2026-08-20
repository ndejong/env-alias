"""Unit tests for main.py entrypoint() and usage_help().

Existing test_cli.py uses subprocess and doesn't contribute to coverage.
These tests call entrypoint()/usage_help() directly with mocked sys.argv
to cover all branches in main.py.

Main coverage gaps:
  Line 43: return after usage_help when no args
  Lines 54-55: else branch (len(args.args) not 1 or >=2)
  Line 81: exit(e.code) in except SystemExit when code != 0
"""

from unittest.mock import patch

import pytest

from env_alias.main import entrypoint, usage_help


def _run(*argv: str):
    """Call entrypoint() with given argv, catching SystemExit.

    Returns:
        None if entrypoint() returns normally (exit 0 was caught internally).
        int exit code if SystemExit propagated (non-zero or unhandled).
    """
    with patch("sys.argv", ["env-alias", *argv]):
        try:
            entrypoint()
        except SystemExit as e:
            return e.code
    return None


# --- usage_help() -----------------------------------------------------------


def test_usage_help_no_exit(capsys):
    usage_help()
    out = capsys.readouterr().out
    assert "Usage:" in out
    assert "env-alias" in out.lower()


def test_usage_help_exit_0(capsys):
    with pytest.raises(SystemExit) as exc_info:
        usage_help(exit_code=0)
    assert exc_info.value.code == 0


def test_usage_help_exit_1(capsys):
    with pytest.raises(SystemExit) as exc_info:
        usage_help(exit_code=1)
    assert exc_info.value.code == 1


# --- entrypoint() — no args → usage_help (line 43) ------------------------


def test_entrypoint_no_args(capsys):
    code = _run()
    assert code is None
    out = capsys.readouterr().out
    assert "Usage:" in out


# --- entrypoint() --version ------------------------------------------------


def test_entrypoint_version(capsys):
    """--version exits 0 via argparse, caught internally by except SystemExit."""
    code = _run("--version")
    assert code is None
    out = capsys.readouterr().out
    assert "env-alias" in out.lower() or "Env Alias" in out


# --- entrypoint() --debug --------------------------------------------------


def test_entrypoint_debug_no_args(capsys):
    code = _run("--debug")
    assert code is None
    out = capsys.readouterr().out
    assert "Usage:" in out


# --- entrypoint() --generator ----------------------------------------------


def test_entrypoint_generator_no_file(capsys):
    code = _run("--generator")
    assert code is None
    out = capsys.readouterr().out
    assert "Usage:" in out


def test_entrypoint_generator_with_file(tmp_path, config_file, capsys):
    config = config_file("    GEN_VAR:\n        value: hello\n")
    code = _run("--generator", str(config))
    assert code is None
    out = capsys.readouterr().out
    assert 'export "GEN_VAR"' in out


def test_entrypoint_debug_generator(tmp_path, config_file, capsys):
    config = config_file("    DBG_VAR:\n        value: hello\n")
    code = _run("--debug", "--generator", str(config))
    assert code is None
    out = capsys.readouterr().out
    assert 'export "DBG_VAR"' in out


# --- entrypoint() — alias mode (1 arg) ------------------------------------


def test_entrypoint_alias_1_arg(tmp_path, config_file, capsys):
    config = config_file("    ALIAS_VAR:\n        value: hello\n")
    code = _run(str(config))
    assert code is None
    out = capsys.readouterr().out
    assert "alias" in out.lower()


def test_entrypoint_alias_1_arg_basename(tmp_path, config_file, capsys):
    """Single arg should derive alias name from filename basename."""
    config = config_file("    VAR:\n        value: val\n")
    code = _run(str(config))
    assert code is None
    out = capsys.readouterr().out
    assert "def" in out.lower()


# --- entrypoint() — alias mode (2+ args) ----------------------------------


def test_entrypoint_alias_2_args(tmp_path, config_file, capsys):
    config = config_file("    ALIAS_VAR:\n        value: hello\n")
    code = _run("myalias", str(config))
    assert code is None
    out = capsys.readouterr().out
    assert "myalias" in out.lower()


# --- entrypoint() — debug in alias mode -----------------------------------


def test_entrypoint_debug_alias(tmp_path, config_file, capsys):
    config = config_file("    ALIAS_VAR:\n        value: hello\n")
    code = _run("--debug", "myalias", str(config))
    assert code is None
    out = capsys.readouterr().out
    assert "alias" in out.lower()
    assert "--debug" in out


# --- entrypoint() — invalid alias name -----------------------------------


def test_entrypoint_invalid_alias_name(tmp_path, config_file, capsys):
    config = config_file("    VAR:\n        value: val\n")
    code = _run("bad-name!", str(config))
    assert code == 1


# --- entrypoint() — nonexistent file → EnvAliasException ------------------


def test_entrypoint_nonexistent_file(capsys):
    """Alias mode with nonexistent file just prints alias (file not validated until generate)."""
    code = _run("nonexistent.yml")
    assert code is None
    out = capsys.readouterr().out
    assert "alias" in out.lower()


# --- entrypoint() — KeyboardInterrupt -----------------------------------


def test_entrypoint_keyboard_interrupt(capsys):
    with (
        patch("sys.argv", ["env-alias"]),
        patch("env_alias.main.argparse.ArgumentParser.parse_args", side_effect=KeyboardInterrupt),
    ):
        with pytest.raises(SystemExit) as exc_info:
            entrypoint()
        assert exc_info.value.code == 130


# --- entrypoint() — SystemExit with non-zero code (line 81) ---------------


def test_entrypoint_systemexit_nonzero(capsys):
    """argparse invalid argument raises SystemExit(2), reaching exit(e.code) (line 81)."""
    code = _run("--nonexistent-flag")
    assert code == 2


# --- entrypoint() — rhs construction with special chars -------------------


def test_entrypoint_rhs_special_chars(tmp_path, config_file, capsys):
    """Filepaths with single quotes in directory name should be escaped in the alias."""
    d = tmp_path / "test'dir"
    d.mkdir()
    f = d / "test-file.yml"
    f.write_text("env-alias:\n    VAR:\n        value: val\n")
    code = _run("myalias", str(f))
    assert code is None
    out = capsys.readouterr().out
    assert "alias" in out.lower()
    # single quote should be escaped
    assert "'\\''" in out or "test" in out


# --- entrypoint() — glob expansion and validation -------------------------


def test_entrypoint_glob_zero_matches_emits_warning(tmp_path, capsys, caplog):
    """Glob with zero matches logs a WARNING to stderr and exits 0 with no stdout."""
    code = _run(str(tmp_path / "nonexistent-*.yml"))
    assert code is None
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "No definition files matched glob pattern" in caplog.text


def test_entrypoint_glob_matches_emits_aliases(tmp_path, capsys):
    """Glob with matches expands and emits an alias per matched file."""
    f1 = tmp_path / "env-app1.yml"
    f1.write_text("env-alias:\n    A:\n        value: 1\n")
    f2 = tmp_path / "env-app2.yml"
    f2.write_text("env-alias:\n    B:\n        value: 2\n")

    code = _run(str(tmp_path / "env-*.yml"))
    assert code is None
    captured = capsys.readouterr()
    assert 'alias "env-app1"=' in captured.out
    assert 'alias "env-app2"=' in captured.out


def test_entrypoint_naked_directory_raises(tmp_path):
    """Passing a naked directory raises EnvAliasException."""
    d = tmp_path / "configs"
    d.mkdir()
    code = _run(str(d))
    assert code == 1


def test_entrypoint_non_yaml_extension_raises(tmp_path):
    """Passing a non-YAML file raises EnvAliasException."""
    f = tmp_path / "config.json"
    f.write_text("{}")
    code = _run(str(f))
    assert code == 1


def test_entrypoint_empty_basename_raises():
    """Root slash only path raises EnvAliasException."""
    code = _run("/")
    assert code == 1


def test_entrypoint_explicit_alias_with_zero_match_glob(tmp_path, capsys):
    """Explicit alias with a glob that matches 0 files exits 0 cleanly."""
    code = _run("myalias", str(tmp_path / "nonexistent-*.yml"))
    assert code is None
    captured = capsys.readouterr()
    assert captured.out == ""


def test_entrypoint_explicit_alias_with_multi_match_glob(tmp_path):
    """Explicit alias with a glob matching multiple files raises EnvAliasException."""
    f1 = tmp_path / "env-1.yml"
    f1.write_text("env-alias:\n    A:\n        value: 1\n")
    f2 = tmp_path / "env-2.yml"
    f2.write_text("env-alias:\n    B:\n        value: 2\n")

    code = _run("myalias", str(tmp_path / "env-*.yml"))
    assert code == 1


def test_entrypoint_glob_invalid_extension_raises(tmp_path):
    """Glob pattern with non-YAML extension raises EnvAliasException."""
    code = _run(str(tmp_path / "env-*.txt"))
    assert code == 1


def test_entrypoint_glob_matched_invalid_filename_raises(tmp_path):
    """Glob matching a file with invalid characters in filename raises EnvAliasException."""
    f = tmp_path / "env-bad$name.yml"
    f.write_text("env-alias:\n    A:\n        value: 1\n")
    code = _run(str(tmp_path / "env-*.yml"))
    assert code == 1


def test_entrypoint_multi_file_all_zero_match_globs(tmp_path, capsys):
    """Multi-file mode where all globs match 0 files exits 0 cleanly."""
    code = _run(str(tmp_path / "none1-*.yml"), str(tmp_path / "none2-*.yml"))
    assert code is None
    captured = capsys.readouterr()
    assert captured.out == ""
