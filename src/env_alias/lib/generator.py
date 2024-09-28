import os
import sys
from pathlib import Path
from typing import Dict, Union

from .. import DEFINITIONS_ROOT, LOGGER_LEVEL, LOGGER_NAME
from ..exceptions import EnvAliasException
from ..lib.definitions import EnvAliasDefinitions
from ..lib.logger import logger_get
from ..lib.selector import EnvAliasSelector
from ..lib.source import EnvAliasSource
from ..models.envalias_definition import EnvAliasDefinition
from ..models.sourced_content import SourcedContent

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


class EnvAliasGenerator:
    definitions_file: Path
    values_generated: Dict[str, str] = {}

    def __init__(self, config_file: Path):
        self.definitions_file = config_file

    def generate(self) -> None:
        logger.debug("EnvAliasGenerator.generate()")

        definitions = EnvAliasDefinitions(definitions_root=DEFINITIONS_ROOT).load_definitions(self.definitions_file)
        if not definitions:
            raise EnvAliasException(f"Empty or malformed {self.definitions_file=}")

        for definition in definitions:
            is_existing_setting = os.getenv(definition.name) or self.values_generated.get(definition.name)
            if definition.override is False and is_existing_setting:
                logger.debug(f"Skipping {definition.name!r} because already set and definition.override=False.")
                continue

            value = self.get_definition_value(definition=self.update_env_replacement_attributes(definition))

            if value is not None:  # NB: not just "if value" because value could be a valid empty string
                self.values_generated[definition.name] = value
                os.environ[definition.name] = str(value)  # exists at this process and sub-process only

                if definition.value_to:
                    if definition.value_to == "<stderr>":
                        print(value, file=sys.stderr)
                    elif definition.value_to == "<stdout>":
                        print(value, file=sys.stdout)
                    else:
                        raise EnvAliasException("Unsupported 'value_to' value encountered.")

                if definition._is_internal_only is True:
                    logger.debug(
                        f"Definition for {definition.name!r} defines a 'null' name for env-alias internal "
                        f"only use, skipping generated output."
                    )
                    continue

                self.output_export(env_name=definition.name, env_value=value)

                if definition.ansible_vault_password_file:  # special additional output case
                    self.output_export(
                        env_name=self.values_generated[value], env_value=definition.ansible_vault_password
                    )

    def output_export(self, env_name: str, env_value: Union[str, None] = "", output_prefix: str = " ") -> None:
        output = f'{output_prefix}export "{env_name}"="{env_value}"'
        logger.debug(f"output={output!r}")
        print(output, file=sys.stdout)  # NB: force stdout

    def get_definition_value(self, definition: EnvAliasDefinition) -> Union[str, None]:
        logger.debug(f"EnvAliasGenerator.get_definition_value({definition.name=}, ...)")

        if definition.value:
            return definition.value

        sourced_content = self.get_content_from_source(definition=definition)

        parser = sourced_content.content_type
        if definition.parser:
            parser = definition.parser

        if sourced_content.source_method in ("getpass", "stdin", "keepass") or parser == "none":
            return sourced_content.content

        if definition.selector == "none":
            return None

        if parser == "ini":
            return EnvAliasSelector.ini_content(sourced_content.content, definition.selector)
        elif parser == "json":
            return EnvAliasSelector.json_content(sourced_content.content, definition.selector)
        elif parser in ["yaml", "yml"]:
            return EnvAliasSelector.yaml_content(sourced_content.content, definition.selector)

        if definition.selector and not str(definition.selector).isdigit():
            raise EnvAliasException(f"Selector for plaintext content must be number {definition.selector=}")
        elif definition.selector is None:
            definition.selector = "1"

        return EnvAliasSelector.text_content(sourced_content.content, selector=int(definition.selector))

    def get_content_from_source(self, definition: EnvAliasDefinition) -> SourcedContent:
        if definition.source and definition.source.startswith("http"):
            sourced_content = EnvAliasSource.remote(url=definition.source)

        elif definition.source and definition.source == "<stdin>":
            sourced_content = EnvAliasSource.stdin(prompt=f"Enter {definition.name!r} value using <stdin>: ")

        elif definition.source and definition.source == "<getpass>":
            sourced_content = EnvAliasSource.getpass(prompt=f"Enter {definition.name!r} value using <getpass>: ")

        elif definition.source and definition.keepass_password:
            sourced_content = EnvAliasSource.keepass(
                filename=Path(definition.source), password=definition.keepass_password, selector=definition.selector
            )

        elif definition.source and definition.ansible_vault_password:
            sourced_content = EnvAliasSource.ansible_vault(
                filename=Path(definition.source), password=definition.ansible_vault_password
            )

        elif definition.ansible_vault_password and definition.ansible_vault_password_file:
            sourced_content = EnvAliasSource.ansible_vault_password_file(password=definition.ansible_vault_password)
            self.values_generated[sourced_content.content] = sourced_content.source  # for the special additional output

        elif definition.source:
            sourced_content = EnvAliasSource.local(filename=Path(definition.source))

        elif definition.exec:
            sourced_content = EnvAliasSource.execute(command_line=definition.exec)

        else:
            raise EnvAliasException(f"Definition for env-alias {definition.name!r} is malformed.")

        return sourced_content

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
