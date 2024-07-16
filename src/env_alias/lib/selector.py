import configparser
import json
from functools import reduce
from typing import Union

import yaml

from ..exceptions import EnvAliasException


class EnvAliasSelector:
    @staticmethod
    def text_content(content: str, selector: int) -> str:
        lines = content.replace("\r", "").split("\n")
        if len(lines) < int(selector):
            raise EnvAliasException(f"Text content selector {selector!r} is out of range; text has {len(lines)} lines.")

        return lines[int(selector) - 1]

    @staticmethod
    def ini_content(content: str, selector_path: Union[str, None]) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'ini' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path).split(".")

        if len(selector_paths) != 2:
            raise EnvAliasException('Selector path for INI content must be in the form "<section>.<option>" only.')

        try:
            config = configparser.ConfigParser()
            config.read_string(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the INI content data provided.", detail=e)

        selector_section, selector_option = selector_paths

        try:
            return config.get(selector_section, selector_option)
        except Exception as e:
            raise EnvAliasException('Unable to locate "<section>.<option>" in INI content provided.', detail=e)

    @staticmethod
    def json_content(content: str, selector_path: Union[str, None]) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'json' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path)

        try:
            data = json.loads(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the JSON content data provided.", detail=e)

        try:
            return EnvAliasSelector.__data_select(data, selector_paths)
        except Exception as e:
            raise EnvAliasException("Unable to find data at supplied path in JSON content.", detail=e)

    @staticmethod
    def yaml_content(content: str, selector_path: Union[str, None]) -> str:
        if not selector_path:
            raise EnvAliasException("Selector not provided; must define a 'selector' for 'yaml' parsing.")

        selector_paths = EnvAliasSelector.__parse_selector_path(selector_path)

        try:
            data = yaml.safe_load(content)
        except Exception as e:
            raise EnvAliasException("Unable to parse and load the YAML content data provided.", detail=e)

        try:
            return EnvAliasSelector.__data_select(data, selector_paths)
        except Exception as e:
            raise EnvAliasException("Unable to find data at supplied path in YAML content.", detail=e)

    @staticmethod
    def __data_select(root: str, path: str, sep: str = ".") -> str:
        return reduce(lambda acc, nxt: acc[nxt], [int(x) if x.isdigit() else x for x in path.split(sep)], root)  # type: ignore[index]

    @staticmethod
    def __parse_selector_path(selector_path: str) -> str:
        selector_path = selector_path.replace("/", ".")
        return ("." + selector_path.replace("[", ".").replace("]", ".")).replace("..", ".")[1:]
