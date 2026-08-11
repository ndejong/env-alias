"""Typed constants for magic strings used across the codebase."""

from enum import Enum


class SourceMethod(str, Enum):
    """Methods by which content is sourced."""

    GETPASS = "getpass"
    STDIN = "stdin"
    KEEPASS = "keepass"
    LOCAL = "local"
    REMOTE = "remote"
    EXECUTE = "execute"
    ANSIBLE_VAULT = "ansible_vault"
    ANSIBLE_VAULT_PASSWORD_FILE = "ansible_vault_password_file"


class ParserType(str, Enum):
    """Content parser types."""

    NONE = "none"
    YAML = "yaml"
    YML = "yml"
    JSON = "json"
    INI = "ini"


class ContentType(str, Enum):
    """Content types for sourced content."""

    TEXT = "text"
    INI = "ini"
    JSON = "json"
    YAML = "yaml"


class SelectorType(str, Enum):
    """Selector special values."""

    NONE = "none"


class ValueTo(str, Enum):
    """value_to target destinations.

    ``<stdout>`` was removed in 0.7.0: writing raw text into the sourced stdout
    stream was unsafe/meaningless, so only ``<stderr>`` remains a valid target.
    """

    STDERR = "<stderr>"
