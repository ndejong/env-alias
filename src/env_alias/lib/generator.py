import os
import re
import sys
from pathlib import Path

from .. import DEFINITIONS_ROOT, LOGGER_LEVEL, LOGGER_NAME
from ..exceptions import EnvAliasException
from ..lib.definitions import EnvAliasDefinitions
from ..lib.logger import logger_get
from ..lib.selector import PARSER_STRATEGIES, EnvAliasSelector
from ..lib.source import SOURCE_STRATEGIES, _secrets_to_redact
from ..models.constants import ContentType, ParserType, SelectorType, SourceMethod, ValueTo
from ..models.envalias_definition import EnvAliasDefinition
from ..models.sourced_content import SourcedContent

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)

_ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Map content types to their corresponding parser types for PARSER_STRATEGIES lookup
_CONTENT_TO_PARSER: dict[ContentType, ParserType] = {
    ContentType.JSON: ParserType.JSON,
    ContentType.INI: ParserType.INI,
    ContentType.YAML: ParserType.YAML,
    ContentType.TEXT: ParserType.NONE,
}


def _redact_secrets(text: str, secrets: dict[str, str]) -> str:
    """Replace secret values with <redacted> in debug output."""
    redacted = text
    for value in secrets.values():
        if value and len(value) > 2:
            redacted = redacted.replace(value, "<redacted>")
    return redacted


def _sh_single_quote(s: str) -> str:
    """POSIX single-quote ``s`` unconditionally.

    Inside single quotes the shell performs no expansion, so this is the only
    quoting mode that safely carries arbitrary secret values (passwords with
    ``"``, ``$``, `` ` ``, ``\\``, newlines, ...) into the user's shell without
    corruption or command injection. A literal single quote is escaped by
    closing the quote, emitting an escaped ``\\'``, and reopening.
    """
    return "'" + s.replace("'", "'\\''") + "'"


class EnvAliasGenerator:
    definitions_files: list[Path]
    values_generated: dict[str, str]
    source_map: dict[str, str]

    def __init__(self, config_file: Path | list[Path]):
        if isinstance(config_file, Path):
            self.definitions_files = [config_file]
        else:
            self.definitions_files = config_file
        self.values_generated = {}
        self.source_map = {}

    def generate(self) -> None:
        logger.debug("EnvAliasGenerator.generate()")

        for config_file in self.definitions_files:
            self._generate_from_file(config_file)

    def _generate_from_file(self, config_file: Path) -> None:
        definitions = EnvAliasDefinitions(definitions_root=DEFINITIONS_ROOT).load_definitions(config_file)
        if not definitions:
            raise EnvAliasException(f"Empty or malformed {config_file=}")

        # All-or-nothing output: buffer every export line and flush only after
        # every definition resolves successfully. A failure on definition 5 of
        # 10 must NOT leave 4 exports on stdout — the tool's output is consumed
        # as `source <(env-alias ...)`, so partial output means a partially-set
        # environment with the shell reporting success (P0-4).
        buffered_exports: list[str] = []

        for definition in definitions:
            is_existing_setting = definition.name in os.environ or definition.name in self.values_generated
            if definition.override is False and is_existing_setting:
                logger.debug(f"Skipping {definition.name!r} because already set and definition.override=False.")
                continue

            value = self.get_definition_value(definition=self.update_env_replacement_attributes(definition))

            if value is not None:  # NB: not just "if value" because value could be a valid empty string
                self.values_generated[definition.name] = value
                _secrets_to_redact[definition.name] = value
                os.environ[definition.name] = str(value)  # exists at this process and sub-process only

                if definition.value_to:
                    if definition.value_to == ValueTo.STDERR:
                        print(value, file=sys.stderr)
                    else:
                        # '<stdout>' is rejected at the model; this guards any
                        # other invalid value defensively.
                        raise EnvAliasException("Unsupported 'value_to' value encountered.")

                if definition.is_internal_only is True:
                    logger.debug(
                        f"Definition for {definition.name!r} defines a 'null' name for env-alias internal "
                        f"only use, skipping generated output."
                    )
                    continue

                buffered_exports.append(self.build_export(env_name=definition.name, env_value=value))

                if definition.ansible_vault_password_file:  # special additional output case
                    buffered_exports.append(
                        self.build_export(
                            env_name=self.source_map[value],
                            env_value=definition.ansible_vault_password,
                        )
                    )

        # All definitions resolved — flush the buffered export lines now.
        for line in buffered_exports:
            print(line, file=sys.stdout)

    def build_export(self, env_name: str, env_value: str | None = "", output_prefix: str = " ") -> str:
        if not _ENV_NAME_RE.fullmatch(env_name):
            raise EnvAliasException(
                f"Invalid environment variable name {env_name!r}: must match ^[A-Za-z_][A-Za-z0-9_]*$"
            )
        # Value is POSIX single-quoted unconditionally: double quotes would let
        # the shell expand $, `, \, and a literal " would terminate the string
        # — both corrupting the value and enabling command injection (P0-2).
        # The name is double-quoted to preserve the documented output shape
        # (asserted by ~15 tests and intentional shell-history suppression);
        # it is validated above so the double quotes carry no injection risk.
        value_str = "" if env_value is None else str(env_value)
        output = f'{output_prefix}export "{env_name}"={_sh_single_quote(value_str)}'
        logger.debug(f"output={_redact_secrets(output, self.values_generated)!r}")
        return output

    def get_definition_value(self, definition: EnvAliasDefinition) -> str | None:
        logger.debug(f"EnvAliasGenerator.get_definition_value({definition.name=}, ...)")

        if definition.value is not None:
            return definition.value

        sourced_content = self.get_content_from_source(definition=definition)

        parser = sourced_content.content_type
        if definition.parser:
            parser = ParserType(definition.parser) if isinstance(definition.parser, str) else definition.parser

        parser_key = _CONTENT_TO_PARSER.get(parser, ParserType.NONE) if isinstance(parser, ContentType) else parser

        if (
            sourced_content.source_method in (SourceMethod.GETPASS, SourceMethod.STDIN, SourceMethod.KEEPASS)
            or parser == ParserType.NONE
        ):
            return sourced_content.content

        if definition.selector == SelectorType.NONE:
            return None

        parser_fn = PARSER_STRATEGIES.get(parser_key)
        if parser_fn:
            return parser_fn(sourced_content.content, definition.selector)

        if definition.selector and not str(definition.selector).isdigit():
            raise EnvAliasException(f"Selector for plaintext content must be number {definition.selector=}")
        elif definition.selector is None:
            definition.selector = "1"

        return EnvAliasSelector.text_content(sourced_content.content, selector=int(definition.selector))

    def get_content_from_source(self, definition: EnvAliasDefinition) -> SourcedContent:
        for strategy in SOURCE_STRATEGIES:
            if strategy.matches(definition):
                sourced_content = strategy.fetch(definition)

                if sourced_content.source_method == SourceMethod.ANSIBLE_VAULT_PASSWORD_FILE:
                    self.source_map[sourced_content.content] = sourced_content.source

                return sourced_content

        raise EnvAliasException(f"Definition for env-alias {definition.name!r} is malformed.")

    def update_env_replacement_attributes(self, definition: EnvAliasDefinition) -> EnvAliasDefinition:
        attr_names = ["value", "source", "parser", "selector", "keepass_password", "ansible_vault_password"]
        for attr_name in attr_names:
            attr_value = getattr(definition, attr_name)
            if attr_value and str(attr_value).startswith("env:"):
                setattr(definition, attr_name, self.get_replacement_env_value(attr_value))
        return definition

    def get_replacement_env_value(self, value: str) -> str:
        env_name = value[4:]

        env_value = os.getenv(env_name, None)
        if env_value is None or len(value) < 1:
            env_value = self.values_generated.get(env_name)

        if env_value is None:
            raise EnvAliasException(f"Definition replacement using {value!r} environment value that is unset.")

        return env_value
