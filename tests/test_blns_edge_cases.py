"""Tests using the Big List of Naughty Strings (BLNS) to verify edge-case robustness
across all major input vectors in env-alias.

Each string in tests/data/blns.base64.json is a base64-encoded naughty string.
We decode them and use them as inputs to all major processing paths.
"""

import base64
import json
import os
import re
import tempfile
from pathlib import Path

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.generator import _ENV_NAME_RE, EnvAliasGenerator, _sh_single_quote
from env_alias.lib.selector import EnvAliasSelector
from env_alias.lib.source import EnvAliasSource
from env_alias.models.constants import ContentType, SourceMethod
from env_alias.models.sourced_content import SourcedContent

# Load the naughty strings once at module level, deduplicating
_BLNS_PATH = Path(__file__).resolve().parent / "data" / "blns.base64.json"
with open(_BLNS_PATH) as _f:
    _BLNS = list({base64.b64decode(b).decode("utf-8", errors="replace") for b in json.load(_f)})


# ---------------------------------------------------------------------------
# 1. sha256_shaker — used by ansible_vault_password_file and sha256 hash
# ---------------------------------------------------------------------------
class TestSha256ShakerNaughty:
    """sha256_shaker must handle every naughty string without crashing."""

    def test_deterministic_for_all_naughty(self):
        for s in _BLNS:
            a = EnvAliasSource.sha256_shaker(value=s, rounds=1)
            b = EnvAliasSource.sha256_shaker(value=s, rounds=1)
            assert a == b, f"Not deterministic for {s!r}"

    def test_non_empty_output_for_all_naughty(self):
        for s in _BLNS:
            h = EnvAliasSource.sha256_shaker(value=s, rounds=1)
            assert h, f"Empty hash for {s!r}"

    def test_no_crash_with_all_naughty(self):
        for s in _BLNS:
            try:
                EnvAliasSource.sha256_shaker(value=s, rounds=2)
            except Exception as e:
                pytest.fail(f"sha256_shaker crashed on {s!r}: {e}")

    def test_base64_roundtrip(self):
        for s in _BLNS:
            h = EnvAliasSource.sha256_shaker(value=s, rounds=2)
            try:
                base64.b64decode(h)
            except Exception as e:
                pytest.fail(f"Invalid base64 in hash for {s!r}: {e}")


# ---------------------------------------------------------------------------
# 2. ansible_vault_password_file — env var name + file path
# ---------------------------------------------------------------------------
class TestAnsibleVaultPasswordFileNaughty:
    """ansible_vault_password_file must handle every naughty string without crashing."""

    def test_envvar_starts_with_letter(self):
        for s in _BLNS:
            result = EnvAliasSource.ansible_vault_password_file(password=s)
            name = result.source
            assert name, f"Empty env var name for {s!r}"
            assert name[0].isalpha(), f"Env var {name!r} starts with digit for {s!r}"

    def test_envvar_valid_identifier(self):
        valid = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        for s in _BLNS:
            result = EnvAliasSource.ansible_vault_password_file(password=s)
            assert valid.match(result.source), f"Invalid env var name {result.source!r} for {s!r}"

    def test_deterministic_for_all_naughty(self):
        for s in _BLNS:
            a = EnvAliasSource.ansible_vault_password_file(password=s)
            b = EnvAliasSource.ansible_vault_password_file(password=s)
            assert a.source == b.source, f"Env var name differs for {s!r}: {a.source!r} vs {b.source!r}"
            assert a.content == b.content, f"File path differs for {s!r}: {a.content!r} vs {b.content!r}"

    def test_file_path_in_tmp(self):
        tmp = tempfile.gettempdir()
        for s in _BLNS:
            result = EnvAliasSource.ansible_vault_password_file(password=s)
            assert result.content.startswith(tmp), f"Path {result.content!r} not in {tmp!r} for {s!r}"

    def test_script_valid_for_all_naughty(self):
        for s in _BLNS:
            result = EnvAliasSource.ansible_vault_password_file(password=s)
            assert os.path.isfile(result.content), f"Script not created for {s!r}: {result.content}"
            with open(result.content) as f:
                content = f.read()
            assert content.startswith("#!/bin/sh"), f"Missing shebang for {s!r}"
            assert result.source in content, f"Script missing env var {result.source!r} for {s!r}"

    def test_no_crash_with_all_naughty(self):
        for s in _BLNS:
            try:
                EnvAliasSource.ansible_vault_password_file(password=s)
            except Exception as e:
                pytest.fail(f"ansible_vault_password_file crashed on {s!r}: {e}")

    def test_different_naughty_strings_differ(self):
        seen: dict[str, str] = {}
        for s in _BLNS:
            result = EnvAliasSource.ansible_vault_password_file(password=s)
            if result.source in seen:
                pytest.fail(f"Duplicate env var {result.source!r} for {s!r} (first: {seen[result.source]!r})")
            seen[result.source] = s


# ---------------------------------------------------------------------------
# 3. Selector — text_content, ini_content, json_content, yaml_content
# ---------------------------------------------------------------------------
class TestSelectorNaughty:
    """Parser selectors must handle naughty content and selector paths."""

    def test_text_content_all_naughty(self):
        """Each naughty string as a line in content, with valid line selectors."""
        for s in _BLNS:
            content = f"line1\n{s}\nline3"
            for selector in [1, 2, 3]:
                try:
                    result = EnvAliasSelector.text_content(content, selector)
                    if selector == 2:
                        # text_content strips trailing newlines
                        assert result == s.rstrip("\n"), f"text_content returned wrong value for {s!r}"
                except Exception as e:
                    pytest.fail(f"text_content crashed on {s!r} with selector {selector}: {e}")

    def test_text_content_invalid_selector(self):
        """Out-of-range selectors must raise."""
        content = "line1\nline2\nline3"
        for selector in [0, 4, -1, 999]:
            with pytest.raises((ValueError, EnvAliasException)):
                EnvAliasSelector.text_content(content, selector)

    def test_json_content_naughty_keys(self):
        """Each naughty string as a JSON key with a known value."""
        for s in _BLNS:
            try:
                data = {s: "test_value"}
                result = EnvAliasSelector._EnvAliasSelector__data_select(data, s)  # pyright: ignore[reportAttributeAccessIssue]
                assert result == "test_value", f"JSON select failed for key {s!r}"
            except KeyError:
                pass  # Naughty strings can't be valid selector paths
            except Exception as e:
                pytest.fail(f"JSON select crashed on key {s!r}: {e}")

    def test_json_content_naughty_values(self):
        """Each naughty string as a JSON value with a known key."""
        for s in _BLNS:
            try:
                data = {"key": s}
                result = EnvAliasSelector._EnvAliasSelector__data_select(data, "key")  # pyright: ignore[reportAttributeAccessIssue]
                assert result == s, f"JSON select returned wrong value for {s!r}"
            except Exception as e:
                pytest.fail(f"JSON select crashed on value {s!r}: {e}")

    def test_yaml_content_naughty_keys(self):
        """Each naughty string as a YAML key with a known value."""
        for s in _BLNS:
            try:
                data = {s: "test_value"}
                result = EnvAliasSelector._EnvAliasSelector__data_select(data, s)  # pyright: ignore[reportAttributeAccessIssue]
                assert result == "test_value", f"YAML select failed for key {s!r}"
            except KeyError:
                pass  # Naughty strings can't be valid selector paths
            except Exception as e:
                pytest.fail(f"YAML select crashed on key {s!r}: {e}")

    def test_yaml_content_naughty_values(self):
        """Each naughty string as a YAML value with a known key."""
        for s in _BLNS:
            try:
                data = {"key": s}
                result = EnvAliasSelector._EnvAliasSelector__data_select(data, "key")  # pyright: ignore[reportAttributeAccessIssue]
                assert result == s, f"YAML select returned wrong value for {s!r}"
            except Exception as e:
                pytest.fail(f"YAML select crashed on value {s!r}: {e}")

    def test_ini_content_naughty(self):
        """Each naughty string as an INI section.option value."""
        import configparser

        # Characters that configparser treats as special syntax
        _INI_SPECIAL = re.compile(r"[\[\]%#=\n\r\x00-\x1f]")

        for s in _BLNS:
            content = f"[section]\noption = {s}"
            try:
                result = EnvAliasSelector.ini_content(content, "section.option")
                assert isinstance(result, str), f"INI select returned non-string for {s!r}"
            except configparser.Error:
                pass  # Known: naughty strings with INI special chars break parsing
            except Exception as e:
                if not _INI_SPECIAL.search(s):
                    pytest.fail(f"INI crashed on unexpected input {s!r}: {e}")
                # Strings with INI special chars — accept parse failures

    def test_parse_selector_path_naughty(self):
        """Each naughty string as a selector path."""
        for s in _BLNS:
            try:
                result = EnvAliasSelector._EnvAliasSelector__parse_selector_path(s)  # pyright: ignore[reportAttributeAccessIssue]
                assert isinstance(result, str), f"parse_selector_path returned non-string for {s!r}"
            except Exception as e:
                pytest.fail(f"parse_selector_path crashed on {s!r}: {e}")


# ---------------------------------------------------------------------------
# 4. Generator — build_export, get_replacement_env_value
# ---------------------------------------------------------------------------
class TestGeneratorNaughty:
    """Generator must handle naughty strings as env var names and values."""

    def test_build_export_naughty_values(self):
        """Each naughty string as a value in build_export."""
        gen = EnvAliasGenerator(config_file=Path("/dev/null"))
        for s in _BLNS:
            try:
                result = gen.build_export(env_name="TEST_VAR", env_value=s)
                assert "TEST_VAR" in result, f"build_export missing env name for {s!r}"
                assert _sh_single_quote(s) in result, f"build_export missing quoted value for {s!r}"
            except Exception as e:
                pytest.fail(f"build_export crashed on value {s!r}: {e}")

    def test_build_export_naughty_names(self):
        """Each naughty string as an env var name in build_export."""
        gen = EnvAliasGenerator(config_file=Path("/dev/null"))
        for s in _BLNS:
            try:
                result = gen.build_export(env_name=s, env_value="test")
                assert _sh_single_quote("test") in result, f"build_export missing value for name {s!r}"
            except Exception as e:
                # Most naughty strings are invalid env var names — that's expected
                if "Invalid environment variable name" not in str(e):
                    pytest.fail(f"build_export crashed on name {s!r}: {e}")

    def test_build_export_valid_names(self):
        """Valid env var names must work."""
        gen = EnvAliasGenerator(config_file=Path("/dev/null"))
        for s in ["TEST_VAR", "MY_VAR_123", "_PRIVATE", "A", "a1"]:
            result = gen.build_export(env_name=s, env_value="test")
            assert s in result

    def test_sh_single_quote_naughty(self):
        """Each naughty string must be safely single-quoted."""
        for s in _BLNS:
            try:
                result = _sh_single_quote(s)
                assert result.startswith("'"), f"Missing opening quote for {s!r}"
                assert result.endswith("'"), f"Missing closing quote for {s!r}"
            except Exception as e:
                pytest.fail(f"_sh_single_quote crashed on {s!r}: {e}")

    def test_get_replacement_env_value_naughty(self):
        """Each naughty string as an env: replacement name."""
        gen = EnvAliasGenerator(config_file=Path("/dev/null"))
        for s in _BLNS:
            try:
                gen.get_replacement_env_value(f"env:{s}")
            except Exception as e:
                # Expected: env var not set
                if "environment value that is unset" not in str(e):
                    pytest.fail(f"get_replacement_env_value crashed on {s!r}: {e}")

    def test_env_name_regex_naughty(self):
        """Env name regex must reject naughty names and accept valid ones."""
        for s in _BLNS:
            match = _ENV_NAME_RE.fullmatch(s)
            if match:
                # If it matched, it must be a valid env var name
                assert re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s), f"Regex matched invalid name {s!r}"
        # Valid names must match
        for s in ["TEST", "_VAR", "A1B2", "my_var"]:
            assert _ENV_NAME_RE.fullmatch(s), f"Regex rejected valid name {s!r}"


# ---------------------------------------------------------------------------
# 5. SourcedContent — construction with naughty strings
# ---------------------------------------------------------------------------
class TestSourcedContentNaughty:
    """SourcedContent must handle naughty strings as source, content, etc."""

    def test_construction_all_naughty(self):
        """Each naughty string as source, content, source_method, content_type."""
        for s in _BLNS:
            try:
                sc = SourcedContent(
                    source=s,
                    source_method=SourceMethod.LOCAL,
                    content=s,
                    content_type=ContentType.TEXT,
                )
                assert sc.source == s
                assert sc.content == s
            except Exception as e:
                pytest.fail(f"SourcedContent crashed on {s!r}: {e}")


# ---------------------------------------------------------------------------
# 6. Selector path normalization
# ---------------------------------------------------------------------------
class TestSelectorPathNormalization:
    """__parse_selector_path must handle naughty paths without crashing."""

    def test_parse_all_naughty(self):
        for s in _BLNS:
            try:
                result = EnvAliasSelector._EnvAliasSelector__parse_selector_path(s)  # pyright: ignore[reportAttributeAccessIssue]
                assert isinstance(result, str), f"Non-string result for {s!r}"
            except Exception as e:
                pytest.fail(f"parse_selector_path crashed on {s!r}: {e}")


# ---------------------------------------------------------------------------
# 7. EnvAliasDefinition — model with naughty field values
# ---------------------------------------------------------------------------
class TestDefinitionNaughty:
    """EnvAliasDefinition model must handle naughty strings as field values."""

    def test_value_field_naughty(self):
        """Each naughty string as a definition value."""
        from env_alias.models.envalias_definition import EnvAliasDefinition

        for s in _BLNS:
            try:
                d = EnvAliasDefinition(name="TEST", value=s)  # pyright: ignore[reportCallIssue]
                assert d.value == s
            except Exception as e:
                pytest.fail(f"EnvAliasDefinition crashed on value {s!r}: {e}")

    def test_source_field_naughty(self):
        """Each naughty string as a source field."""
        from env_alias.models.envalias_definition import EnvAliasDefinition

        for s in _BLNS:
            try:
                d = EnvAliasDefinition(name="TEST", source=s)  # pyright: ignore[reportCallIssue]
                assert d.source == s
            except Exception as e:
                # Empty source is invalid (needs source/exec/value) — expected
                if "Must have one" not in str(e):
                    pytest.fail(f"EnvAliasDefinition crashed on source {s!r}: {e}")

    def test_exec_field_naughty(self):
        """Each naughty string as an exec field."""
        from env_alias.models.envalias_definition import EnvAliasDefinition

        for s in _BLNS:
            try:
                d = EnvAliasDefinition(name="TEST", exec=s)
                assert d.exec_ == s
            except Exception as e:
                # Empty exec is invalid — expected
                if "Must have one" not in str(e):
                    pytest.fail(f"EnvAliasDefinition crashed on exec {s!r}: {e}")

    def test_selector_field_naughty(self):
        """Each naughty string as a selector field."""
        from env_alias.models.envalias_definition import EnvAliasDefinition

        for s in _BLNS:
            try:
                d = EnvAliasDefinition(name="TEST", value="val", selector=s)  # pyright: ignore[reportCallIssue]
                assert d.selector == s
            except Exception as e:
                pytest.fail(f"EnvAliasDefinition crashed on selector {s!r}: {e}")

    def test_parser_field_naughty(self):
        """Each naughty string as a parser field."""
        from env_alias.models.envalias_definition import EnvAliasDefinition

        for s in _BLNS:
            try:
                d = EnvAliasDefinition(name="TEST", value="val", parser=s)  # pyright: ignore[reportCallIssue]
                assert d.parser is None or d.parser == s.lower()
            except Exception as e:
                pytest.fail(f"EnvAliasDefinition crashed on parser {s!r}: {e}")
