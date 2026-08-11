"""Tests for source strategy resolution order."""

from env_alias.lib.source import SOURCE_STRATEGIES
from env_alias.models.envalias_definition import EnvAliasDefinition


def _make_definition(**kwargs: object) -> EnvAliasDefinition:
    """Create a definition with sensible defaults."""
    defaults: dict[str, object] = {"name": "TEST"}
    defaults.update(kwargs)
    return EnvAliasDefinition(**defaults)  # pyright: ignore[reportArgumentType]


def _resolve_strategy(definition: EnvAliasDefinition) -> str | None:
    """Find the first matching strategy name."""
    for strategy in SOURCE_STRATEGIES:
        if strategy.matches(definition):
            return strategy.name
    return None


class TestStrategyResolution:
    """Test that the correct strategy is selected for various definition combinations."""

    def test_remote_http(self):
        d = _make_definition(source="http://example.com/data.json")
        assert _resolve_strategy(d) == "remote"

    def test_remote_https(self):
        d = _make_definition(source="https://example.com/data.json")
        assert _resolve_strategy(d) == "remote"

    def test_stdin(self):
        d = _make_definition(source="<stdin>")
        assert _resolve_strategy(d) == "stdin"

    def test_getpass(self):
        d = _make_definition(source="<getpass>")
        assert _resolve_strategy(d) == "getpass"

    def test_keepass(self):
        d = _make_definition(source="/path/to/keepass.kdbx", keepass_password="secret")
        assert _resolve_strategy(d) == "keepass"

    def test_ansible_vault(self):
        d = _make_definition(source="/path/to/vault.yml", ansible_vault_password="secret")
        assert _resolve_strategy(d) == "ansible_vault"

    def test_ansible_vault_password_file(self):
        d = _make_definition(ansible_vault_password="secret", ansible_vault_password_file=True)
        assert _resolve_strategy(d) == "ansible_vault_password_file"

    def test_local_file(self):
        d = _make_definition(source="/path/to/config.yml")
        assert _resolve_strategy(d) == "local"

    def test_exec(self):
        d = _make_definition(exec_="echo hello")
        assert _resolve_strategy(d) == "exec"

    def test_keepass_takes_priority_over_local(self):
        """keepass must match before local because local is a catch-all."""
        d = _make_definition(source="/path/to/keepass.kdbx", keepass_password="secret")
        assert _resolve_strategy(d) == "keepass"

    def test_ansible_vault_takes_priority_over_local(self):
        """ansible_vault must match before local."""
        d = _make_definition(source="/path/to/vault.yml", ansible_vault_password="secret")
        assert _resolve_strategy(d) == "ansible_vault"

    def test_http_takes_priority_over_local(self):
        """remote must match before local."""
        d = _make_definition(source="http://example.com/data.txt")
        assert _resolve_strategy(d) == "remote"

    def test_stdin_takes_priority_over_local(self):
        """stdin must match before local."""
        d = _make_definition(source="<stdin>")
        assert _resolve_strategy(d) == "stdin"

    def test_getpass_takes_priority_over_local(self):
        """getpass must match before local."""
        d = _make_definition(source="<getpass>")
        assert _resolve_strategy(d) == "getpass"

    def test_no_strategy_matches_value_only(self):
        """A definition with only value should not match any source strategy."""
        d = _make_definition(value="hello")
        assert _resolve_strategy(d) is None

    def test_strategy_names_are_unique(self):
        """All strategy names should be unique."""
        names = [s.name for s in SOURCE_STRATEGIES]
        assert len(names) == len(set(names))

    def test_strategy_order_is_documented(self):
        """Verify the expected order of strategies for priority correctness."""
        expected_order = [
            "remote",
            "stdin",
            "getpass",
            "keepass",
            "ansible_vault",
            "ansible_vault_password_file",
            "local",
            "exec",
        ]
        actual_order = [s.name for s in SOURCE_STRATEGIES]
        assert actual_order == expected_order
