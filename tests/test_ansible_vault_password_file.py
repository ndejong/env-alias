import os
import secrets
import shutil

import pytest

from env_alias.lib.generator import EnvAliasGenerator
from env_alias.lib.source import EnvAliasSource

pytestmark = [
    pytest.mark.requires_ansible_vault,
    pytest.mark.skipif(
        shutil.which("ansible-vault") is None,
        reason="ansible-vault not found on PATH",
    ),
]

_ITERATIONS_COUNT = 2000


def test_ansiblevault_01(capsys, config_file):
    yaml = """
    password_for_ansible_vault:
        name: null
        source: "tests/data/envalias-ansible-vault-datafile-password.txt"
        selector: 7

    ANSIBLE_VAULT_PASSWORD_FILE:
        ansible_vault_password: "env:password_for_ansible_vault"
        ansible_vault_password_file: true
    """

    f = config_file(yaml)
    EnvAliasGenerator(config_file=f).generate()

    captured = capsys.readouterr().out.rstrip()
    assert "\"='envalias-ansible-test-only-password'" in captured
    assert '"ANSIBLE_VAULT_PASSWORD_FILE"=\'/tmp/' in captured


def test_p1_5_both_orders(capsys, tmp_path):
    """P1-5: both password_file and ansible_vault definitions must work in any order."""
    # A definition file that uses both features with the same password:
    # 1) password_file exports a durable script path
    # 2) ansible_vault decrypts a vault file using that password

    # Order A: password_file first, then ansible_vault
    yaml_a = """
    pw:
        name: null
        source: "tests/data/envalias-ansible-vault-datafile-password.txt"
        selector: 7

    ANSIBLE_VAULT_PASSWORD_FILE:
        ansible_vault_password: "env:pw"
        ansible_vault_password_file: true

    SECRET_FROM_VAULT:
        source: "tests/data/envalias-ansible-vault-datafile.vault"
        ansible_vault_password: "env:pw"
        selector: "all/vars/vault/project_foobar/username"
    """

    # Order B: ansible_vault first, then password_file
    yaml_b = """
    pw:
        name: null
        source: "tests/data/envalias-ansible-vault-datafile-password.txt"
        selector: 7

    SECRET_FROM_VAULT:
        source: "tests/data/envalias-ansible-vault-datafile.vault"
        ansible_vault_password: "env:pw"
        selector: "all/vars/vault/project_foobar/username"

    ANSIBLE_VAULT_PASSWORD_FILE:
        ansible_vault_password: "env:pw"
        ansible_vault_password_file: true
    """

    for label, yaml in [("Order A", yaml_a), ("Order B", yaml_b)]:
        capsys.readouterr()  # clear
        f = tmp_path / f"def_{label}.yml"
        f.write_text("env-alias:\n" + yaml)

        EnvAliasGenerator(config_file=f).generate()

        captured = capsys.readouterr().out

        # Password file export must be present
        assert '"ANSIBLE_VAULT_PASSWORD_FILE"' in captured, f"{label}: missing ANSIBLE_VAULT_PASSWORD_FILE export"

        # Extract the path from the export line
        for line in captured.splitlines():
            if "ANSIBLE_VAULT_PASSWORD_FILE" in line:
                # line looks like:  export "ANSIBLE_VAULT_PASSWORD_FILE"='/tmp/...'
                path = line.split("'")[1]
                assert os.path.isfile(path), f"{label}: exported path does not exist: {path}"
                assert os.access(path, os.X_OK), f"{label}: exported script is not executable: {path}"


def _random_password() -> str:
    """Generate a random password with varied character classes."""
    length = secrets.randbelow(64) + 1  # 1–64 chars
    alphabet = (
        secrets.choice("abcdefghijklmnopqrstuvwxyz")  # start with letter
        + "".join(
            secrets.choice(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:',.<>?/`~ \t\n"
            )
            for _ in range(length - 1)
        )
    )
    return alphabet


class TestSha256Shaker:
    """Verify sha256_shaker properties over many random inputs."""

    def test_deterministic(self):
        """Same input always produces the same output."""
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            a = EnvAliasSource.sha256_shaker(value=pw, rounds=1)
            b = EnvAliasSource.sha256_shaker(value=pw, rounds=1)
            assert a == b, f"sha256_shaker not deterministic for {pw!r}"

    def test_different_passwords_differ(self):
        """Different passwords produce different hashes (collision check)."""
        seen: set[str] = set()
        seen_passwords: set[str] = set()
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            if pw in seen_passwords:
                continue
            seen_passwords.add(pw)
            h = EnvAliasSource.sha256_shaker(value=pw, rounds=2)
            assert h not in seen, f"Collision: {pw!r} -> {h!r}"
            seen.add(h)

    def test_rounds_affect_output(self):
        """Different round counts produce different outputs."""
        pw = _random_password()
        h1 = EnvAliasSource.sha256_shaker(value=pw, rounds=1)
        h2 = EnvAliasSource.sha256_shaker(value=pw, rounds=2)
        h4 = EnvAliasSource.sha256_shaker(value=pw, rounds=4)
        assert h1 != h2
        assert h2 != h4
        assert h1 != h4


class TestAnsibleVaultPasswordFile:
    """Verify ansible_vault_password_file() properties over many random passwords."""

    def test_envvar_starts_with_letter(self):
        """Env var names must always start with a letter (POSIX requirement)."""
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            result = EnvAliasSource.ansible_vault_password_file(password=pw)
            name = result.source
            assert name, f"Empty env var name for password {pw!r}"
            assert name[0].isalpha(), f"Env var {name!r} starts with digit for password {pw!r}"

    def test_envvar_valid_identifier(self):
        """Env var names must be valid shell identifiers (alphanumeric + underscore)."""
        import re

        valid = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            result = EnvAliasSource.ansible_vault_password_file(password=pw)
            assert valid.match(result.source), f"Invalid env var name {result.source!r} for password {pw!r}"

    def test_deterministic_path_and_name(self):
        """Same password always produces the same file path and env var name."""
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            a = EnvAliasSource.ansible_vault_password_file(password=pw)
            b = EnvAliasSource.ansible_vault_password_file(password=pw)
            assert a.source == b.source, f"Env var name differs for same password {pw!r}: {a.source!r} vs {b.source!r}"
            assert a.content == b.content, f"File path differs for same password {pw!r}: {a.content!r} vs {b.content!r}"

    def test_file_path_in_tmp(self):
        """The generated file path must be in the system temp directory."""
        import tempfile

        tmp = tempfile.gettempdir()
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            result = EnvAliasSource.ansible_vault_password_file(password=pw)
            assert result.content.startswith(tmp), f"Path {result.content!r} not in {tmp!r} for password {pw!r}"

    def test_script_content_valid(self):
        """The generated script must be a valid shell script that echoes the env var."""
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            result = EnvAliasSource.ansible_vault_password_file(password=pw)
            script_path = result.content
            assert os.path.isfile(script_path), f"Script not created: {script_path}"
            with open(script_path) as f:
                content = f.read()
            assert content.startswith("#!/bin/sh"), f"Missing shebang in {script_path}"
            assert result.source in content, f"Script does not reference env var {result.source!r} in {script_path}"

    def test_different_passwords_differ(self):
        """Different passwords must produce different env var names and file paths."""
        seen_names: set[str] = set()
        seen_paths: set[str] = set()
        seen_passwords: set[str] = set()
        for _ in range(_ITERATIONS_COUNT):
            pw = _random_password()
            if pw in seen_passwords:
                continue  # skip duplicate random passwords
            seen_passwords.add(pw)
            result = EnvAliasSource.ansible_vault_password_file(password=pw)
            assert result.source not in seen_names, f"Duplicate env var name {result.source!r} for password {pw!r}"
            assert result.content not in seen_paths, f"Duplicate file path {result.content!r} for password {pw!r}"
            seen_names.add(result.source)
            seen_paths.add(result.content)
