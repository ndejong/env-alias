import os
from pathlib import Path
from typing import List, Optional

import yaml

from .. import DEFINITIONS_ROOT, LOGGER_LEVEL, LOGGER_NAME
from ..exceptions import EnvAliasException
from ..lib.logger import logger_get
from ..models.envalias_definition import EnvAliasDefinition

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


class EnvAliasDefinitions:
    definitions_root: str = DEFINITIONS_ROOT

    def __init__(self, definitions_root: Optional[str] = None):
        if definitions_root:
            self.definitions_root = definitions_root

    def load_definitions(self, definitions_file: Path) -> List[EnvAliasDefinition]:
        logger.debug(f"EnvAliasConfig.load_definitions(definitions_file={str(definitions_file)!r})")

        if not os.path.isfile(definitions_file):
            raise EnvAliasException(f"Unable to locate definitions_file={str(definitions_file)!r}")

        loaded_definitions = {}

        with open(definitions_file, "r") as f:
            try:
                loaded_definitions = yaml.safe_load(f.read())
            except yaml.YAMLError as e:
                raise EnvAliasException(f"Failed to load definitions_file={str(definitions_file)!r}", detail=e)

        if not isinstance(loaded_definitions, dict) or self.definitions_root not in loaded_definitions.keys():
            raise EnvAliasException(f"Unable to locate top-level definitions root {self.definitions_root!r}")
        logger.debug(f"Definitions loaded from definitions_file={str(definitions_file)!r}")

        definitions: List[EnvAliasDefinition] = []
        for definition_key, definition_item in loaded_definitions[self.definitions_root].items():
            if not isinstance(definition_item, dict):
                raise EnvAliasException(f"Definition item {definition_key!r} is not dict type")

            definition_item["_filename"] = definitions_file

            if "name" in definition_item.keys() and definition_item["name"] is None:
                definition_item["_is_internal_only"] = True

            if not definition_item.get("name"):
                definition_item["name"] = definition_key

            if definition_item["name"] in ("none", "None"):
                _name = definition_item.get("name")
                logger.warning(f"Definition name is '{_name}' did you mean 'null' instead?")

            try:
                definitions.append(EnvAliasDefinition(**definition_item))
            except TypeError as e:
                raise EnvAliasException(str(e))

            logger.debug(f"Loaded environment definition for {definition_item['name']!r}")

        logger.debug(f"Total {len(definitions)} definitions in {definitions_file=}")
        return definitions
