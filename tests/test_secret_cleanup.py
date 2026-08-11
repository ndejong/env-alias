"""Secret cleanup regression tests.

Secret cleanup was a no-op on the Python side
(``os.unsetenv`` does not update ``os.environ``) and is skipped entirely on
error paths (no ``try/finally``). After a failed keepass/vault fetch, the
password stays in ``os.environ`` and is inherited by every later ``exec:``
step; ``ANSIBLE_VAULT_PASSWORD_FILE`` stays set and the temp password script
is never unlinked.

These tests mock ``EnvAliasSource.execute`` and ``shutil.which`` so they run
without keepassxc-cli or ansible-vault installed.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from env_alias.exceptions import EnvAliasException
from env_alias.lib.source import EnvAliasSource
from env_alias.models.constants import ContentType, SourceMethod
from env_alias.models.sourced_content import SourcedContent

PASSWORD = "super-secret-password-12345"


def _make_fake_file(tmp_path: Path) -> Path:
    f = tmp_path / "data.kdbx"
    f.write_text("dummy")
    return f


def _environ_has_value(value: str) -> str | None:
    """Return the key in os.environ whose value equals `value`, or None."""
    for k, v in os.environ.items():
        if v == value:
            return k
    return None


# ---------------------------------------------------------------------------
# keepass
# ---------------------------------------------------------------------------


def test_keepass_success_cleans_password_from_environ(tmp_path: Path) -> None:
    f = _make_fake_file(tmp_path)
    with (
        patch("env_alias.lib.source.shutil.which", return_value="/usr/bin/keepassxc-cli"),
        patch.object(EnvAliasSource, "_keepass_run", return_value=(0, b"secret-value", b"")),
    ):
        EnvAliasSource.keepass(filename=f, password=PASSWORD, selector="group/entry:Attribute")
    assert _environ_has_value(PASSWORD) is None, "password leaked into os.environ after successful keepass fetch"


def test_keepass_failure_cleans_password_from_environ(tmp_path: Path) -> None:
    f = _make_fake_file(tmp_path)
    with (
        patch("env_alias.lib.source.shutil.which", return_value="/usr/bin/keepassxc-cli"),
        patch.object(EnvAliasSource, "_keepass_run", return_value=(1, b"", b"wrong password")),
        pytest.raises(EnvAliasException),
    ):
        EnvAliasSource.keepass(filename=f, password=PASSWORD, selector="group/entry:Attribute")
    assert _environ_has_value(PASSWORD) is None, "password leaked into os.environ after failed keepass fetch"


def test_keepass_hostile_selector_not_executed(tmp_path: Path) -> None:
    """P1-2: a hostile selector is passed as one argv element, never shell-executed."""
    f = _make_fake_file(tmp_path)
    pwn_file = tmp_path / "ea_pwn"
    hostile_attr = f'att"; touch {pwn_file} ; echo "'

    captured: list[list[str]] = []

    def fake_run(command: list[str], password: str) -> tuple[int, bytes, bytes]:
        captured.append(command)
        return (0, b"ok-value", b"")

    with (
        patch("env_alias.lib.source.shutil.which", return_value="/usr/bin/keepassxc-cli"),
        patch.object(EnvAliasSource, "_keepass_run", side_effect=fake_run),
    ):
        EnvAliasSource.keepass(filename=f, password=PASSWORD, selector=f"group/entry:{hostile_attr}")

    # The hostile attribute was delivered as a single argv element...
    assert captured and hostile_attr in captured[0]
    # ...and was NOT executed as a shell command (no side-effect file).
    assert not pwn_file.exists()
    # The password must not touch os.environ.
    assert _environ_has_value(PASSWORD) is None


# ---------------------------------------------------------------------------
# ansible_vault
# ---------------------------------------------------------------------------


def test_ansible_vault_success_cleans_password_and_file(tmp_path: Path) -> None:
    f = _make_fake_file(tmp_path)
    fake_content = SourcedContent(
        source="cmd",
        source_method=SourceMethod.EXECUTE,
        content="decrypted",
        content_type=ContentType.YAML,
    )
    with (
        patch("env_alias.lib.source.shutil.which", return_value="/usr/bin/ansible-vault"),
        patch.object(EnvAliasSource, "execute", return_value=fake_content),
    ):
        result = EnvAliasSource.ansible_vault(filename=f, password=PASSWORD)
    # Password must not be in os.environ
    assert _environ_has_value(PASSWORD) is None, "password leaked into os.environ after successful vault decrypt"
    # ANSIBLE_VAULT_PASSWORD_FILE must be unset
    assert "ANSIBLE_VAULT_PASSWORD_FILE" not in os.environ, (
        "ANSIBLE_VAULT_PASSWORD_FILE left set after successful vault decrypt"
    )
    # The temp password script must be unlinked
    assert not os.path.isfile(result.content), "temp password script left on disk after successful vault decrypt"


def test_ansible_vault_failure_cleans_password_and_file(tmp_path: Path) -> None:
    f = _make_fake_file(tmp_path)
    # Capture the temp file path before the failure destroys the reference.
    # We patch execute to raise, but ansible_vault_password_file runs first
    # and creates the temp file. We need to find it afterward.
    with (
        patch("env_alias.lib.source.shutil.which", return_value="/usr/bin/ansible-vault"),
        patch.object(EnvAliasSource, "execute", side_effect=EnvAliasException("wrong password")),
        pytest.raises(EnvAliasException),
    ):
        EnvAliasSource.ansible_vault(filename=f, password=PASSWORD)

    # Password must not be in os.environ
    assert _environ_has_value(PASSWORD) is None, "password leaked into os.environ after failed vault decrypt"
    # ANSIBLE_VAULT_PASSWORD_FILE must be unset
    assert "ANSIBLE_VAULT_PASSWORD_FILE" not in os.environ, (
        "ANSIBLE_VAULT_PASSWORD_FILE left set after failed vault decrypt"
    )
    # The temp password script must be unlinked.
    # The filename is derived from sha256_shaker(password, rounds=4) — scan /tmp.
    import glob

    leftover = glob.glob("/tmp/env-alias-vault-*")
    assert not leftover, f"temp password script left on disk after failed vault decrypt: {leftover}"
