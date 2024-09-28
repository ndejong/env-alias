from dataclasses import dataclass
from pathlib import Path
from typing import Union

from ..exceptions import EnvAliasException

_UNSET_SENTINEL = "__unset_sentinel__"
_EXCEPTION_END = "in an env-alias definition."


@dataclass
class EnvAliasDefinition:
    name: str
    _filename: Path

    override: bool = True

    value: Union[str, None] = None
    source: Union[str, None] = None
    exec: Union[str, None] = None

    parser: Union[str, None] = None
    selector: Union[str, None] = _UNSET_SENTINEL
    value_to: Union[str, None] = None

    keepass_password: Union[str, None] = None
    ansible_vault_password: Union[str, None] = None
    ansible_vault_password_file: bool = False

    _is_internal_only: bool = False

    def __post_init__(self) -> None:
        # sanity checks
        if self.exec and self.source:
            raise EnvAliasException(f"Cannot use 'exec' and 'source' {_EXCEPTION_END}")
        if self.exec and self.value:
            raise EnvAliasException(f"Cannot use 'exec' and 'value' {_EXCEPTION_END}")
        if self.source and self.value:
            raise EnvAliasException(f"Cannot use 'source' and 'value' {_EXCEPTION_END}")
        if not self.source and not self.exec and not self.value and not self.ansible_vault_password_file:
            raise EnvAliasException(f"Must have one 'source', 'exec' or 'value' {_EXCEPTION_END}")

        if isinstance(self.value_to, str):
            self.value_to = self.value_to.lower()
            if self.value_to not in ("<stderr>", "<stdout>"):
                raise EnvAliasException(f"Invalid 'value_to' value, must be '<stderr>' or '<stdout>' {_EXCEPTION_END}")

        if self.keepass_password and self.ansible_vault_password:
            raise EnvAliasException(f"Cannot use both 'keepass_password' and 'ansible_vault_password' {_EXCEPTION_END}")
        if self.ansible_vault_password_file and (self.exec or self.source or self.value or self.keepass_password):
            raise EnvAliasException(
                f"Can only use 'ansible_vault_password_file' with 'ansible_vault_password' {_EXCEPTION_END}"
            )
        if self.ansible_vault_password_file and not self.ansible_vault_password:
            raise EnvAliasException(
                f"Must use 'ansible_vault_password_file' with 'ansible_vault_password' {_EXCEPTION_END}"
            )

        # force parser to lower()
        if self.parser:
            self.parser = self.parser.lower()

        # handle selector through the special _UNSET_SENTINEL
        if self.selector and self.selector == _UNSET_SENTINEL:
            self.selector = None
        elif self.selector is None:  # because a "null" that gets cast to None by PyYAML was previously supported
            self.selector = "none"

        # correctly cast 'override' into a bool
        if self.override not in (True, False):
            if str(self.override).lower() in ("false", "no"):
                self.override = False
            elif str(self.override).lower() in ("true", "yes"):
                self.override = True
            else:
                raise EnvAliasException("EnvAliasDefinition.override must be 'true', 'false' only.")

        # correctly cast 'ansible_vault_password_file' into a bool
        if self.ansible_vault_password_file not in (True, False):
            if str(self.ansible_vault_password_file).lower() in ("false", "no"):
                self.ansible_vault_password_file = False
            elif str(self.ansible_vault_password_file).lower() in ("true", "yes"):
                self.ansible_vault_password_file = True
            else:
                raise EnvAliasException("EnvAliasDefinition.ansible_vault_password_file must be 'true', 'false' only.")
