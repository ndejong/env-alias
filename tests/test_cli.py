"""CLI entry-point regression tests.

Drives ``entrypoint()`` through the installed ``env-alias`` binary via subprocess
to cover argument parsing, mode selection, debug output, and exit codes. Every
test in this file would have caught either P0-8 (--debug crash) or P1-6
(--generator no-file crash) before they shipped.
"""

import subprocess
from pathlib import Path


def _env_alias_bin() -> str:
    import shutil

    bin_path = shutil.which("env-alias")
    assert bin_path is not None, "env-alias executable not found on PATH"
    return bin_path


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_env_alias_bin(), *args],
        capture_output=True,
        text=True,
    )


# --- P1-6: --generator with no positional args must not traceback ----------


def test_generator_no_args_exits_cleanly():
    """P1-6 regression: --generator with no file must print usage, exit 0, no traceback."""
    result = _run("--generator")
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}\nstderr={result.stderr!r}"
    assert "Usage:" in result.stdout or "Usage:" in result.stderr
    assert "Traceback" not in result.stderr


def test_bare_env_alias_exits_cleanly():
    """env-alias with no args must print usage, exit 0, no traceback."""
    result = _run()
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}\nstderr={result.stderr!r}"
    assert "Usage:" in result.stdout or "Usage:" in result.stderr
    assert "Traceback" not in result.stderr


# --- P0-8: --debug must not crash ------------------------------------------


def test_debug_generator_no_crash(tmp_path: Path, config_file):
    """P0-8 regression: --debug --generator must succeed with debug output on stderr."""
    config = config_file("    DBG_VAR:\n        value: hello\n")
    result = _run("--debug", "--generator", str(config))
    assert result.returncode == 0, f"exit {result.returncode}\nstderr={result.stderr!r}"
    assert "Traceback" not in result.stderr
    assert 'export "DBG_VAR"' in result.stdout
    # debug output should appear on stderr (at least the logger line)
    assert "DEBUG" in result.stderr or "debug" in result.stderr.lower()


def test_debug_alias_mode_no_crash(tmp_path: Path, config_file):
    """P0-8 regression: --debug <alias> <file> must emit alias line without crashing."""
    config = config_file("    ALIAS_VAR:\n        value: world\n")
    result = _run("--debug", "myalias", str(config))
    assert result.returncode == 0, f"exit {result.returncode}\nstderr={result.stderr!r}"
    assert "Traceback" not in result.stderr
    assert "alias" in result.stdout.lower()


# --- version flag ----------------------------------------------------------


def test_version_exits_zero():
    result = _run("--version")
    assert result.returncode == 0
    assert "Env Alias" in result.stdout or "env-alias" in result.stdout.lower()


# --- error paths -----------------------------------------------------------


def test_bad_alias_name_exits_1(tmp_path: Path, config_file):
    """Invalid alias name must exit 1 with no traceback."""
    config = config_file("    VAR:\n        value: val\n")
    result = _run("bad-name!", str(config))
    assert result.returncode == 1
    assert "Traceback" not in result.stderr


def test_missing_file_exits_1(tmp_path: Path):
    """--generator with a nonexistent file must exit 1 with no traceback."""
    result = _run("--generator", str(tmp_path / "nope.yml"))
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
