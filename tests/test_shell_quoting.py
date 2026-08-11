"""Shell-quoting regression tests for generated ``export`` output.

The tool's stdout is consumed by the user's interactive shell via
``source <(env-alias --generator ...)``. Any value interpolated into that
output without POSIX-correct quoting is a shell-injection vector: a
secret containing ``"`` corrupts the value and executes attacker-controlled
code.

The primary guard is a direct unit test on ``EnvAliasGenerator.output_export``
that sources the emitted line in a real ``bash`` subprocess and asserts the
round-tripped value is byte-identical to the input and that no side-effect
file was created. A secondary integration test drives the full generator
pipeline end-to-end.
"""

import contextlib
import io
import subprocess
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator

HOSTILE_VALUES = [
    pytest.param('pw"; touch /tmp/env_alias_pwned; echo "', id="double-quote-injection"),
    pytest.param("single'quote", id="single-quote"),
    pytest.param("back`tick`substitution", id="backtick-command-substitution"),
    pytest.param("dollar$var", id="dollar-variable"),
    pytest.param("$(id)", id="dollar-paren-command-substitution"),
    pytest.param("back\\slash", id="backslash-escape"),
    pytest.param("semi;colon", id="semicolon"),
    pytest.param("line1\nline2", id="newline"),
    pytest.param("  leading-and-trailing  ", id="surrounding-spaces"),
    pytest.param("", id="empty-string"),
    pytest.param("UTF-8: café—日本語", id="utf-8"),
    pytest.param("tab\tchar", id="tab"),
    pytest.param("hash#dollar$amp&", id="mixed-shell-special"),
]


def _make_generator() -> EnvAliasGenerator:
    gen = EnvAliasGenerator.__new__(EnvAliasGenerator)
    gen.values_generated = {}
    return gen


def _emit(gen: EnvAliasGenerator, name: str, value: str) -> str:
    return gen.build_export(env_name=name, env_value=value)


def _source_in_bash(script: str, var_name: str) -> str:
    """Source ``script`` in a real bash and return the exported value of ``var_name``."""
    full = script + f"\nprintf '%s' \"${{{var_name}}}\"\n"
    result = subprocess.run(
        ["bash", "-c", full],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"bash sourcing failed (rc={result.returncode}):\nscript={script!r}\nstderr={result.stderr}"
    )
    return result.stdout


@pytest.mark.parametrize("value", HOSTILE_VALUES)
def test_output_export_round_trips_byte_identical(value: str, tmp_path: Path) -> None:
    gen = _make_generator()
    name = "HOSTILE_VALUE"
    output = _emit(gen, name, value)
    round_tripped = _source_in_bash(output, name)
    assert round_tripped == value, (
        f"round-trip mismatch for value={value!r}\ngenerated={output!r}\nround_tripped={round_tripped!r}"
    )
    # No side-effect file should appear anywhere under tmp_path (injection guard).
    assert not list(tmp_path.iterdir()), f"injection created files: {list(tmp_path.iterdir())}"


def test_invalid_env_var_name_rejected() -> None:
    """A name not matching ^[A-Za-z_][A-Za-z0-9_]*$ must raise, not be emitted."""
    gen = _make_generator()
    with pytest.raises(EnvAliasException):
        gen.build_export(env_name="bad-name!", env_value="x")


def test_output_shape_safe_value() -> None:
    """Safe values keep the documented shape: leading space, double-quoted name, single-quoted value."""
    gen = _make_generator()
    output = _emit(gen, "SAFE_NAME", "safevalue")
    assert output.rstrip() == " export \"SAFE_NAME\"='safevalue'"


def test_generator_pipeline_round_trips(tmp_path: Path, config_file):
    """End-to-end: a hostile value sourced from real generator output must round-trip."""
    hostile = 'pw"; echo INJECTED'
    yaml_body = f"    PIPELINE_HOSTILE:\n        value: {hostile!r}\n"
    f = config_file(yaml_body)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        EnvAliasGenerator(config_file=f).generate()
    output = buf.getvalue()

    round_tripped = _source_in_bash(output, "PIPELINE_HOSTILE")
    assert round_tripped == hostile, f"pipeline round-trip mismatch\noutput={output!r}\ngot={round_tripped!r}"
