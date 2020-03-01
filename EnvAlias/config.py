
import os
import yaml

from . import logger


class EnvAliasConfigException(Exception):
    pass


class EnvAliasConfig:

    debug = None
    config = None
    config_root = None

    def __init__(self, config_root, debug=False):
        self.debug = debug
        self.config_root = config_root

    def load_config(self, configuration_file, return_config=False):
        if configuration_file is None or not os.path.isfile(configuration_file):
            raise EnvAliasConfigException('Unable to locate configuration file', configuration_file)
        self.config = self.__load_config(configuration_file)
        if return_config:
            return self.config

    def __load_config(self, config_filename):
        loaded_config = {}

        with open(config_filename, 'r') as f:
            try:
                loaded_config = yaml.safe_load(f.read())
            except yaml.YAMLError as e:
                raise EnvAliasConfigException(e)

        def replace_env_values(input):
            if input is None:
                return input
            elif type(input) in (int, bool):
                return input
            elif type(input) is str:
                if input.lower()[0:4] == 'env:':
                    env_name = input.replace('env:', '')
                    logger.debug('Config element set via env value {}'.format(env_name))
                    value = os.getenv(env_name, None)
                    if value is None or len(value) < 1:
                        raise EnvAliasConfigException('Config requested env value not set', env_name)
                    return value
                return input
            elif type(input) is list:
                r = []
                for item in input:
                    r.append(replace_env_values(item))
                return r
            elif type(input) is dict:
                r = {}
                for item_k, item_v in input.items():
                    r[item_k] = replace_env_values(item_v)
                return r
            else:
                raise EnvAliasConfigException('Unsupported type in replace_env_values()', input)

        loaded_config = replace_env_values(loaded_config)

        if type(loaded_config) is not dict or self.config_root not in loaded_config.keys():
            raise EnvAliasConfigException('Unable to locate config root', self.config_root)

        return loaded_config[self.config_root]
