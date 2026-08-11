import configparser
import json
from collections.abc import Callable
from functools import reduce
from typing import Any

import yaml

from ..exceptions import EnvAliasException
from ..models.constants import ParserType


class EnvAliasSelector:
    @staticmethod
    def text_content(content: str, selector: int) -> str:
        lines = content.replace("\r", "").rstrip("\n").split("\n")
        s = int(selector)
        if s < 1 or s > len(lines):
            raise EnvAliasException(f"Text content selector {selector!r} is out of range; text has {len(lines)} lines.")

        return lines[s - 1]

    @staticmethod
    def ini_content(content: str, selector_path: str | None) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'ini' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path).split(".")

        if len(selector_paths) != 2:
            raise EnvAliasException('Selector path for INI content must be in the form "<section>.<option>" only.')

        try:
            config = configparser.ConfigParser()
            config.read_string(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the INI content data provided.", detail=e) from e

        selector_section, selector_option = selector_paths

        try:
            return config.get(selector_section, selector_option)
        except Exception as e:
            raise EnvAliasException('Unable to locate "<section>.<option>" in INI content provided.', detail=e) from e

    @staticmethod
    def json_content(content: str, selector_path: str | None) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'json' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path)

        try:
            data = json.loads(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the JSON content data provided.", detail=e) from e

        try:
            return EnvAliasSelector.__data_select(data, selector_paths)
        except Exception as e:
            raise EnvAliasException("Unable to find data at supplied path in JSON content.", detail=e) from e

    @staticmethod
    def yaml_content(content: str, selector_path: str | None) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'yaml' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path)

        try:
            data = yaml.safe_load(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the YAML content data provided.", detail=e) from e

        try:
            return EnvAliasSelector.__data_select(data, selector_paths)
        except Exception as e:
            raise EnvAliasException("Unable to find data at supplied path in YAML content.", detail=e) from e

    @staticmethod
    def __data_select(root: Any, path: str, sep: str = ".") -> str:
        parts = [int(x) if x.isdigit() and x.isascii() else x for x in path.split(sep)]
        result = reduce(lambda acc, nxt: acc[nxt], parts, root)
        if not isinstance(result, (str, int, float, bool)):
            raise EnvAliasException(f"Selection resolved to {type(result).__name__}, but only scalars are supported.")
        return str(result)

    @staticmethod
    def __parse_selector_path(selector_path: str) -> str:
        selector_path = selector_path.replace("/", ".")
        return ("." + selector_path.replace("[", ".").replace("]", ".")).replace("..", ".")[1:]


PARSER_STRATEGIES: dict[ParserType, Callable[[str, str | None], str]] = {
    ParserType.INI: EnvAliasSelector.ini_content,
    ParserType.JSON: EnvAliasSelector.json_content,
    ParserType.YAML: EnvAliasSelector.yaml_content,
    ParserType.YML: EnvAliasSelector.yaml_content,
}
