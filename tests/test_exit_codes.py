"""Exit-code and all-or-nothing output regression tests.

Failures must exit with a non-zero status instead of 0, avoiding the bug where
a failure produced an empty alias with status 0. Because the tool's output is
consumed as ``source <(env-alias --generator ...)``, a status of 0 means the
user's shell reports success while zero variables were exported — the classic
"credentials silently unset" failure.

Additionally, ``generate()`` printed export lines incrementally, so a failure
on definition 5 of 10 left 4 exports already on stdout. The fix buffers all
export lines and writes them only after every definition resolves.
"""

import contextlib
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator


def _env_alias_bin() -> str:
    bin_path = shutil.which("env-alias")
    assert bin_path is not None, "env-alias executable not found on PATH"
    return bin_path


def _run_cli(config_file: Path) -> subprocess.CompletedProcess:
    """Run env-alias --generator via subprocess and return the result."""
    return subprocess.run(
        [_env_alias_bin(), "--generator", str(config_file)],
        capture_output=True,
        text=True,
    )


def test_exit_code_success(tmp_path: Path, config_file) -> None:
    config = config_file("    OK_VAR:\n        value: hello\n")
    result = _run_cli(config)
    assert result.returncode == 0, result.stderr


def test_exit_code_malformed_yaml(tmp_path: Path) -> None:
    f = tmp_path / "bad.yml"
    f.write_text("env-alias:\n  BAD: [unclosed")
    result = _run_cli(f)
    assert result.returncode != 0, f"expected non-zero exit, got {result.returncode}"


def test_exit_code_missing_file(tmp_path: Path) -> None:
    result = _run_cli(tmp_path / "nonexistent.yml")
    assert result.returncode != 0, f"expected non-zero exit, got {result.returncode}"


def test_exit_code_failing_exec(tmp_path: Path, config_file) -> None:
    config = config_file("    FAIL_EXEC:\n        exec: 'unknown-cmd-XYZ'\n")
    result = _run_cli(config)
    assert result.returncode != 0, f"expected non-zero exit, got {result.returncode}"


# test_exit_code_unknown_parser deferred to P1-4: an unknown parser currently
# silently succeeds with the raw value rather than raising, which is a
# selector/parser edge case, not an exit-code defect.


def test_all_or_nothing_on_failure(tmp_path: Path, config_file) -> None:
    """A definition file where the last entry fails must emit NO export lines."""
    config = config_file(
        "    FIRST:\n        value: should_not_appear\n    SECOND:\n        exec: 'definitely-unknown-cmd-XYZ'\n",
    )
    result = _run_cli(config)
    assert result.returncode != 0
    assert "export" not in result.stdout, f"partial output leaked on failure:\nstdout={result.stdout!r}"


def test_all_or_nothing_in_generate(tmp_path: Path, config_file) -> None:
    """Unit-level: generate() must not print anything if a later definition fails."""
    config = config_file(
        "    FIRST:\n        value: should_not_appear\n    SECOND:\n        exec: 'definitely-unknown-cmd-XYZ'\n",
    )
    buf = io.StringIO()
    with pytest.raises(EnvAliasException), contextlib.redirect_stdout(buf):
        EnvAliasGenerator(config_file=config).generate()
    assert "export" not in buf.getvalue(), f"partial output leaked on failure:\nstdout={buf.getvalue()!r}"


def test_exit_code_invalid_alias_name():
    """P0-6: invalid alias name must exit 1 with no traceback in stderr."""
    bin_path = _env_alias_bin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as tmp:
        tmp.write("env-alias:\n  VAR: {value: val}")
        tmp_path = Path(tmp.name)

    try:
        result = subprocess.run(
            [bin_path, "bad-name!", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Traceback" not in result.stderr
    finally:
        tmp_path.unlink()
