import os
import yaml

from env_alias.utils import logger
from env_alias.exceptions import EnvAliasException


class EnvAliasConfig:

    debug = None
    config = None
    config_root = None

    def __init__(self, config_root, debug=False):
        self.debug = debug
        self.config_root = config_root

    def load_config(self, configuration_file, return_config=False):
        if configuration_file is None or not os.path.isfile(configuration_file):
            raise EnvAliasException("Unable to locate configuration file", configuration_file)
        logger.debug("Loading config: {}".format(configuration_file))
        self.config = self.__load_config(configuration_file)
        if return_config:
            return self.config

    def __load_config(self, config_filename):
        loaded_config = {}

        with open(config_filename, "r") as f:
            try:
                loaded_config = yaml.safe_load(f.read())
            except yaml.YAMLError as e:
                raise EnvAliasException(e)

        def replace_env_values(input_value):
            if input_value is None:
                return input_value
            elif isinstance(input_value, int) or isinstance(input_value, bool):
                return input_value
            elif isinstance(input_value, str):
                if input_value.lower()[0:4] == "env:":
                    env_name = input_value.replace("env:", "")
                    logger.debug("Config element set via env value {}".format(env_name))
                    value = os.getenv(env_name, None)
                    if value is None or len(value) < 1:
                        raise EnvAliasException("Config requested env value not set", env_name)
                    return value
                return input_value
            elif isinstance(input_value, list):
                r = []
                for item in input_value:
                    r.append(replace_env_values(item))
                return r
            elif isinstance(input_value, dict):
                r = {}
                for item_k, item_v in input_value.items():
                    r[item_k] = replace_env_values(item_v)
                return r
            else:
                raise EnvAliasException("Unsupported type in replace_env_values()", input_value)

        loaded_config = replace_env_values(loaded_config)

        if not isinstance(loaded_config, dict) or self.config_root not in loaded_config.keys():
            raise EnvAliasException("Unable to locate config root", self.config_root)

        logger.debug("Config successfully loaded: {}".format(config_filename))
        return loaded_config[self.config_root]
