"""Verify the installed/tooling version consistency and docs coverage (P3-7, P3-8)."""

from importlib import metadata
from pathlib import Path

import pytest

import env_alias
from env_alias.models.envalias_definition import EnvAliasDefinition

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DOCS_ATTRS_DIR = _PROJECT_ROOT / "docs" / "docs" / "definition-attributes"

# Attributes the model accepts that are user-facing definition attributes with a
# dedicated docs page. Internal bookkeeping fields (filename, is_internal_only)
# are excluded from the nav/attribute gap check.
_USER_ATTR_TO_DOC = {
    "name": "name.md",
    "value": "value.md",
    "source": "source.md",
    "exec_": "exec.md",
    "parser": "parser.md",
    "selector": "selector.md",
    "value_to": "value-to.md",
    "override": "override.md",
    "keepass_password": "keepass-password.md",
    "ansible_vault_password": "ansible-vault-password.md",
    "ansible_vault_password_file": "ansible-vault-password-file.md",
}
_INTERNAL_FIELDS = {"filename", "is_internal_only"}


def test_installed_version_matches_sources() -> None:
    """importlib.metadata.version('env-alias') must equal env_alias.__version__.

    P3-8: the version is single-sourced from src/env_alias/__init__.py via
    [tool.hatch.version] path; this asserts the built/installed distribution
    matches the source constant.
    """
    assert metadata.version("env-alias") == env_alias.__version__


def test_every_model_field_has_docs_page() -> None:
    """Every user-facing EnvAliasDefinition field must have a definition-attributes doc page.

    P3-7: a new attribute without documentation should fail CI.
    """
    model_fields = set(EnvAliasDefinition.model_fields) - _INTERNAL_FIELDS
    assert model_fields == set(_USER_ATTR_TO_DOC), (
        "model fields changed; update _USER_ATTR_TO_DOC / _INTERNAL_FIELDS:\n"
        f"  fields without docs mapping: {sorted(model_fields - set(_USER_ATTR_TO_DOC))}"
    )
    for field, doc_file in _USER_ATTR_TO_DOC.items():
        assert field in model_fields
        assert (_DOCS_ATTRS_DIR / doc_file).is_file(), f"missing docs page: {doc_file}"


def test_all_attribute_docs_pages_are_expected() -> None:
    """Definition-attributes pages must not drift from the model (no orphaned pages)."""
    actual_pages = {p.name for p in _DOCS_ATTRS_DIR.glob("*.md")}
    expected_pages = set(_USER_ATTR_TO_DOC.values())
    assert actual_pages == expected_pages, (
        f"unexpected doc pages {sorted(actual_pages - expected_pages)} "
        f"or missing {sorted(expected_pages - actual_pages)}"
    )


@pytest.mark.skipif(
    not (_PROJECT_ROOT / "docs" / "mkdocs.yml").is_file(),
    reason="mkdocs.yml not present",
)
def test_nav_covers_every_attribute(mkdocs_nav) -> None:
    """Every user-facing attribute doc page must appear in the mkdocs nav (P3-7)."""
    nav_basenames = {Path(entry).name for entry in mkdocs_nav}
    for doc_file in _USER_ATTR_TO_DOC.values():
        assert doc_file in nav_basenames, f"attribute doc {doc_file!r} missing from docs/mkdocs.yml nav"
