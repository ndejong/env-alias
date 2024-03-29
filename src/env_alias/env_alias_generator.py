from env_alias import __title__
from env_alias import __version__

from env_alias.utils.logger import Logger
from env_alias.utils.config import EnvAliasConfig
from env_alias.utils.content import EnvAliasContent
from env_alias.utils.selector import EnvAliasSelector
from env_alias.exceptions import EnvAliasException


logger = Logger(name=__title__).logging


class EnvAliasGenerator:
    def __init__(self, logger_level="warning"):
        Logger(name=__title__).setup(level=logger_level)
        logger.info(f"{__title__} v{__version__}")

    def main(self, configuration_file=None, no_space=False) -> None:

        if isinstance(configuration_file, list):
            configuration_file = configuration_file[0]

        config = EnvAliasConfig(config_root=__title__, configuration_file=configuration_file).config

        if not config:
            raise EnvAliasException("Empty configuration provided")

        for config_k, config_v in config.items():
            env_name = config_k
            if "name" in config_v.keys():
                env_name = config_v["name"]
            output_prefix = " "  # prevents shell command history
            if no_space is True:
                output_prefix = ""

            setting_value = self.get_setting(config_k, config_v)
            if setting_value is not None:
                output = '{}export "{}"="{}"'.format(output_prefix, env_name, setting_value)
                logger.debug(output)
                print(output)

    def get_setting(self, config_key, config):
        logger.debug(f"{__name__} get_setting(config_key={config_key} <config>)")

        if "value" in config.keys():
            return config["value"]
        elif "source" in config.keys() and config["source"][0:4] == "http":
            content, content_type = EnvAliasContent.remote(config["source"])
        elif "source" in config.keys():
            content, content_type = EnvAliasContent.local(config["source"])
        elif "exec" in config.keys():
            content, content_type = EnvAliasContent.execute(config["exec"])
        else:
            raise EnvAliasException('Configuration of env-alias item "{}" is malformed'.format(config_key))

        parser = content_type
        if "parser" in config.keys():
            parser = config["parser"].lower()

        selector = None
        if "selector" in config.keys():
            if config["selector"] is None or config["selector"] == "null":
                selector = "none"  # edge case where "selector" exists and set to none (or null)
            else:
                selector = config["selector"]

        if parser == "ini":
            return EnvAliasSelector.ini_content(content, selector)
        elif parser == "json":
            return EnvAliasSelector.json_content(content, selector)
        elif parser in ["yaml", "yml"]:
            return EnvAliasSelector.yaml_content(content, selector)

        return EnvAliasSelector.text_content(content, selector)
