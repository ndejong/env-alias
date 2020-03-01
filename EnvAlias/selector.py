
import json
import yaml
import configparser
from functools import reduce


class EnvAliasSelectorException(Exception):
    pass


class EnvAliasSelector:

    @staticmethod
    def text_content(content, selector):
        if selector is None or len(str(selector)) == 0:
            selector = 1
        elif str(selector).lower() == 'null' or str(selector).lower() == 'none':
            return None

        return content.split('\n')[int(selector)-1].replace('\r','')

    @staticmethod
    def ini_content(content, selector_path):
        selector_path = EnvAliasSelector.__parse_selector_path(selector_path, 'INI').split('.')

        if len(selector_path) != 2:
            raise EnvAliasSelectorException('Selector path for INI content must be in the form "<section>.<option>" only.')

        try:
            config = configparser.ConfigParser()
            config .read_string(content)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to parse and load the INI content data provided.', e)

        selector_section, selector_option = selector_path

        try:
            return config.get(selector_section, selector_option)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to locate "<section>.<option>" in INI content provided.', e)

    @staticmethod
    def json_content(content, selector_path):
        selector_path = EnvAliasSelector.__parse_selector_path(selector_path, 'JSON')

        try:
            data = json.loads(content)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to parse and load the JSON content data provided.', e)

        try:
            return EnvAliasSelector.__data_select(data, selector_path)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to find data at supplied path in JSON content.', e)

    @staticmethod
    def yaml_content(content, selector_path):
        selector_path = EnvAliasSelector.__parse_selector_path(selector_path, 'YAML')

        try:
            data = yaml.safe_load(content)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to parse and load the YAML content data provided.', e)

        try:
            return EnvAliasSelector.__data_select(data, selector_path)
        except(Exception) as e:
            raise EnvAliasSelectorException('Unable to find data at supplied path in YAML content.', e)

    @staticmethod
    def __data_select(root, path, sep='.'):
        return reduce(
            lambda acc, nxt: acc[nxt],[int(x) if x.isdigit() else x for x in path.split(sep)], root
        )

    @staticmethod
    def __parse_selector_path(selector_path, content_type):
        if selector_path is None or len(str(selector_path)) == 0:
            raise EnvAliasSelectorException('Selector required for {} content type, check the configuration '
                                    'has a "selector" value.'.format(content_type))
        return ('.' + selector_path.replace('[','.').replace(']','.')).replace('..','.')[1:]
