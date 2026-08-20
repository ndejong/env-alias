"""Tests for multi-file definition support.

Allows: env-alias file01.yml file02.yml file03.yml
- Generator mode: each file is processed independently; all exports are combined.
- Alias mode: a single invocation emits one alias per file (name inferred per
  file's basename), each lazily generating only its own file.
"""

import contextlib
import io
from unittest.mock import patch

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import EnvAliasGenerator
from env_alias.main import entrypoint


def _run(*argv: str):
    with patch("sys.argv", ["env-alias", *argv]):
        try:
            entrypoint()
        except SystemExit as e:
            return e.code
    return None


def _find_alias_lines(stdout: str) -> list[str]:
    return [line.strip() for line in stdout.strip().splitlines() if line.startswith("alias ")]


# ---------------------------------------------------------------------------
# Generator-level tests
# ---------------------------------------------------------------------------


class TestGeneratorMultiFile:
    def test_two_files_both_exported(self, tmp_path, config_file):
        f1 = config_file("    VAR_A:\n        value: from_file1\n")
        f2 = tmp_path / "file2.yml"
        f2.write_text("env-alias:\n    VAR_B:\n        value: from_file2\n")

        gen = EnvAliasGenerator(config_file=[f1, f2])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.generate()
        out = buf.getvalue()
        assert 'export "VAR_A"' in out
        assert 'export "VAR_B"' in out

    def test_three_files_all_exported(self, tmp_path, config_file):
        f1 = config_file("    A:\n        value: '1'\n")
        f2 = tmp_path / "b.yml"
        f2.write_text("env-alias:\n    B:\n        value: '2'\n")
        f3 = tmp_path / "c.yml"
        f3.write_text("env-alias:\n    C:\n        value: '3'\n")

        gen = EnvAliasGenerator(config_file=[f1, f2, f3])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.generate()
        out = buf.getvalue()
        assert 'export "A"' in out
        assert 'export "B"' in out
        assert 'export "C"' in out

    def test_output_order_matches_file_order(self, tmp_path, config_file):
        f1 = config_file("    FIRST:\n        value: '1'\n")
        f2 = tmp_path / "second.yml"
        f2.write_text("env-alias:\n    SECOND:\n        value: '2'\n")

        gen = EnvAliasGenerator(config_file=[f1, f2])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.generate()
        lines = [line.strip() for line in buf.getvalue().strip().splitlines() if "export" in line]
        assert lines[0].startswith('export "FIRST"')
        assert lines[1].startswith('export "SECOND"')

    def test_single_file_backward_compat(self, tmp_path, config_file):
        f1 = config_file("    SOLO:\n        value: only\n")
        gen = EnvAliasGenerator(config_file=f1)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.generate()
        assert 'export "SOLO"' in buf.getvalue()

    def test_one_file_fails_raises(self, tmp_path, config_file):
        f1 = config_file("    OK_VAR:\n        value: ok\n")
        f2 = tmp_path / "bad.yml"
        f2.write_text("env-alias:\n    FAIL:\n        exec: 'definitely-unknown-cmd-XYZ'\n")

        gen = EnvAliasGenerator(config_file=[f1, f2])
        with pytest.raises(EnvAliasException):
            gen.generate()

    def test_second_file_sees_first_files_env(self, tmp_path, config_file):
        """env: references from file2 should resolve values set by file1."""
        f1 = config_file("    SECRET:\n        value: mysecret\n")
        f2 = tmp_path / "file2.yml"
        f2.write_text("env-alias:\n    USE_SECRET:\n        value: 'env:SECRET'\n")

        gen = EnvAliasGenerator(config_file=[f1, f2])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gen.generate()
        out = buf.getvalue()
        assert 'export "USE_SECRET"' in out
        assert "mysecret" in out

    def test_empty_file_raises(self, tmp_path):
        f = tmp_path / "empty.yml"
        f.write_text("env-alias:\n")

        gen = EnvAliasGenerator(config_file=f)
        with pytest.raises(EnvAliasException):
            gen.generate()

    def test_multi_file_empty_one_raises(self, tmp_path, config_file):
        f1 = config_file("    OK:\n        value: ok\n")
        f2 = tmp_path / "empty.yml"
        f2.write_text("env-alias:\n")

        gen = EnvAliasGenerator(config_file=[f1, f2])
        with pytest.raises(EnvAliasException):
            gen.generate()


# ---------------------------------------------------------------------------
# CLI / entrypoint-level tests
# ---------------------------------------------------------------------------


class TestEntrypointMultiFile:
    def test_multi_file_alias_mode(self, tmp_path, config_file, capsys):
        f1 = config_file("    VAR_A:\n        value: a\n")
        f2 = tmp_path / "file2.yml"
        f2.write_text("env-alias:\n    VAR_B:\n        value: b\n")
        f3 = tmp_path / "dir.yml"
        f3.write_text("env-alias:\n    VAR_C:\n        value: c\n")

        code = _run(str(f1), str(f2), str(f3))
        assert code is None
        # One alias per file, name inferred from each file's own basename.
        # config_file fixture names the file "def.yml" -> alias "def".
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 3
        assert any('alias "def"="' in a for a in aliases)
        assert any('alias "file2"="' in a for a in aliases)
        assert any('alias "dir"="' in a for a in aliases)
        # Each alias's RHS generates only its own file.
        assert any(str(f1) in a and str(f2) not in a and str(f3) not in a for a in aliases)
        assert any(str(f2) in a and str(f1) not in a and str(f3) not in a for a in aliases)
        assert any(str(f3) in a and str(f1) not in a and str(f2) not in a for a in aliases)

    def test_explicit_alias_single_file(self, tmp_path, config_file, capsys):
        f1 = config_file("    VAR_A:\n        value: a\n")

        code = _run("myalias", str(f1))
        assert code is None
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 1
        assert 'alias "myalias"="' in aliases[0]

    def test_hyphenated_alias_name_accepted(self, tmp_path, config_file, capsys):
        # Alias names (unlike env var names) may contain hyphens, e.g. the
        # README's `env-awesome-vars` example. Both inferred and explicit names.
        f1 = config_file("    VAR_A:\n        value: a\n")
        f2 = tmp_path / "env-awesome-vars.yml"
        f2.write_text("env-alias:\n    VAR_B:\n        value: b\n")

        code = _run(str(f2))
        assert code is None
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 1
        assert 'alias "env-awesome-vars"="' in aliases[0]

        # Multi-file: each hyphenated basename becomes a valid alias.
        code = _run(str(f1), str(f2))
        assert code is None
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 2

        # Explicit hyphenated alias is also fine.
        code = _run("env-proj", str(f1))
        assert code is None

    def test_explicit_alias_multi_file_raises(self, tmp_path, config_file):
        f1 = config_file("    VAR_A:\n        value: a\n")
        f2 = tmp_path / "file2.yml"
        f2.write_text("env-alias:\n    VAR_B:\n        value: b\n")

        # An explicit alias name plus multiple files is ambiguous -> error.
        code = _run("myalias", str(f1), str(f2))
        assert code == 1

    def test_generator_mode_multi_file(self, tmp_path, config_file):
        f1 = config_file("    GEN_A:\n        value: a\n")
        f2 = tmp_path / "gen2.yml"
        f2.write_text("env-alias:\n    GEN_B:\n        value: b\n")

        buf = io.StringIO()
        with patch("sys.argv", ["env-alias", "--generator", str(f1), str(f2)]), contextlib.redirect_stdout(buf):
            entrypoint()
        out = buf.getvalue()
        assert 'export "GEN_A"' in out
        assert 'export "GEN_B"' in out

    def test_generator_mode_single_file_matches_alias_rhs(self, tmp_path, config_file, capsys):
        f1 = config_file("    SOLO:\n        value: solo\n")

        # The RHS an alias emits must round-trip: --generator '<file>' yields
        # exactly that file's exports.
        code = _run(str(f1))
        assert code is None
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 1
        assert f"--generator '{f1}'" in aliases[0]

        buf = io.StringIO()
        with patch("sys.argv", ["env-alias", "--generator", str(f1)]), contextlib.redirect_stdout(buf):
            entrypoint()
        assert 'export "SOLO"' in buf.getvalue()


# ---------------------------------------------------------------------------
# Subprocess-level tests (installed binary)
# ---------------------------------------------------------------------------


class TestCliMultiFile:
    def test_multi_file_nonexistent_files_emits_aliases(self, tmp_path, capsys):
        """Non-existent definition files still emit aliases without disk access."""
        f1 = tmp_path / "env-host1.yml"
        f2 = tmp_path / "env-host2.yml"
        # Neither file exists on disk
        code = _run(str(f1), str(f2))
        assert code is None
        aliases = _find_alias_lines(capsys.readouterr().out)
        assert len(aliases) == 2
        assert any('alias "env-host1"=' in a for a in aliases)
        assert any('alias "env-host2"=' in a for a in aliases)

    def test_multi_file_subprocess(self, tmp_path, config_file):
        import shutil
        import subprocess

        bin_path = shutil.which("env-alias")
        if bin_path is None:
            pytest.skip("env-alias not installed")

        f1 = config_file("    CLI_A:\n        value: a\n")
        f2 = tmp_path / "cli2.yml"
        f2.write_text("env-alias:\n    CLI_B:\n        value: b\n")

        result = subprocess.run(
            [bin_path, "--generator", str(f1), str(f2)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert 'export "CLI_A"' in result.stdout
        assert 'export "CLI_B"' in result.stdout

    def test_alias_mode_multi_file_subprocess(self, tmp_path, config_file):
        import shutil
        import subprocess

        bin_path = shutil.which("env-alias")
        if bin_path is None:
            pytest.skip("env-alias not installed")

        f1 = config_file("    ALIAS_A:\n        value: a\n")
        f2 = tmp_path / "alias2.yml"
        f2.write_text("env-alias:\n    ALIAS_B:\n        value: b\n")

        result = subprocess.run(
            [bin_path, str(f1), str(f2)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        aliases = _find_alias_lines(result.stdout)
        assert len(aliases) == 2
        # One alias per file, each referencing only its own file.
        assert any('alias "def"="' in a for a in aliases)
        assert any('alias "alias2"="' in a for a in aliases)
        assert not any(str(f1) in a and str(f2) in a for a in aliases)
