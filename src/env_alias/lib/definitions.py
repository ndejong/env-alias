import os
from pathlib import Path

import yaml
from pydantic import ValidationError

from .. import DEFINITIONS_ROOT, LOGGER_LEVEL, LOGGER_NAME
from ..exceptions import EnvAliasException
from ..lib.logger import logger_get
from ..models.envalias_definition import EnvAliasDefinition

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


class EnvAliasDefinitions:
    definitions_root: str = DEFINITIONS_ROOT

    def __init__(self, definitions_root: str | None = None):
        if definitions_root:
            self.definitions_root = definitions_root

    def load_definitions(self, definitions_file: Path) -> list[EnvAliasDefinition]:
        logger.debug(f"EnvAliasConfig.load_definitions(definitions_file={str(definitions_file)!r})")

        if not os.path.isfile(definitions_file):
            raise EnvAliasException(f"Unable to locate definitions_file={str(definitions_file)!r}")

        loaded_definitions = {}

        with open(definitions_file) as f:
            try:
                loaded_definitions = yaml.safe_load(f.read())
            except yaml.YAMLError as e:
                raise EnvAliasException(f"Failed to load definitions_file={str(definitions_file)!r}", detail=e) from e

        if not isinstance(loaded_definitions, dict) or self.definitions_root not in loaded_definitions:
            raise EnvAliasException(f"Unable to locate top-level definitions root {self.definitions_root!r}")

        # The root value must itself be a mapping (e.g. a file containing only
        # `env-alias:` parses to a null root, which must not crash downstream
        # with an AttributeError on .items()). P0-6 expects a clean exception.
        root = loaded_definitions[self.definitions_root]
        if not isinstance(root, dict):
            raise EnvAliasException(f"Empty or malformed definitions root {self.definitions_root!r}")
        logger.debug(f"Definitions loaded from definitions_file={str(definitions_file)!r}")

        definitions: list[EnvAliasDefinition] = []
        for definition_key, definition_item in root.items():
            if not isinstance(definition_item, dict):
                raise EnvAliasException(f"Definition item {definition_key!r} is not dict type")

            is_internal_only = "name" in definition_item and definition_item["name"] is None

            if not definition_item.get("name"):
                definition_item["name"] = definition_key

            if definition_item["name"] in ("none", "None"):
                logger.warning(f"Definition name is '{definition_item['name']}' did you mean 'null' instead?")

            if "selector" not in definition_item:
                definition_item["selector"] = None
            elif definition_item["selector"] is None:
                definition_item["selector"] = "none"

            try:
                definition = EnvAliasDefinition(**definition_item)
            except ValidationError as e:
                raise EnvAliasException(f"Invalid definition for {definition_key!r}: {e}") from e

            definition.filename = definitions_file
            definition.is_internal_only = is_internal_only
            definitions.append(definition)

            logger.debug(f"Loaded environment definition for {definition.name!r}")

        logger.debug(f"Total {len(definitions)} definitions in {definitions_file=}")
        return definitions
