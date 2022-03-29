import os
import yaml

from env_alias import __title__
from env_alias.utils.logger import Logger
from env_alias.exceptions import EnvAliasException


logger = Logger(name=__title__).logging


class EnvAliasConfig:

    config_root = None
    configuration_file = None
    __config = None

    def __init__(self, config_root, configuration_file):
        self.config_root = config_root
        self.configuration_file = configuration_file

    @property
    def config(self):
        if self.__config:
            return self.__config

        if self.configuration_file is None or not os.path.isfile(self.configuration_file):
            raise EnvAliasException("Unable to locate configuration file", self.configuration_file)

        self.__config = self.__load_config()
        return self.__config

    def __load_config(self):
        logger.debug(f"{__name__} __load_config() - configuration_file={self.configuration_file}")

        loaded_config = {}

        with open(self.configuration_file, "r") as f:
            try:
                loaded_config = yaml.safe_load(f.read())
            except yaml.YAMLError as e:
                raise EnvAliasException(e)

        loaded_config = EnvAliasConfig.replace_env_values(loaded_config)

        if not isinstance(loaded_config, dict) or self.config_root not in loaded_config.keys():
            raise EnvAliasException("Unable to locate config root", self.config_root)

        logger.debug(f"Config successfully loaded: {self.configuration_file}")
        return loaded_config[self.config_root]

    @staticmethod
    def replace_env_values(input_value):

        if input_value is None:
            return None

        elif isinstance(input_value, int) or isinstance(input_value, bool):
            return input_value

        elif isinstance(input_value, str):
            if input_value.lower()[0:4] == "env:":
                env_name = input_value.replace("env:", "")
                logger.debug(f"Config element set via env value {env_name}")
                value = os.getenv(env_name, None)
                if value is None or len(value) < 1:
                    raise EnvAliasException("Config requested env value not set", env_name)
                return value
            return input_value

        elif isinstance(input_value, list):
            r = []
            for item in input_value:
                r.append(EnvAliasConfig.replace_env_values(item))
            return r

        elif isinstance(input_value, dict):
            r = {}
            for item_k, item_v in input_value.items():
                r[item_k] = EnvAliasConfig.replace_env_values(item_v)
            return r

        raise EnvAliasException("Unsupported type in replace_env_values()", input_value)
