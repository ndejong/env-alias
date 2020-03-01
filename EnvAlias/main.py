
from . import NAME
from . import VERSION

from . import logger

from . import EnvAliasConfig
from . import EnvAliasContent
from . import EnvAliasSelector


class EnvAliasException(Exception):
    pass


class EnvAlias:

    def __init__(self, logger_level='warning'):
        logger.init(name=NAME, level=logger_level)
        logger.info('{} v{}'.format(NAME, VERSION))

    def main(self, configuration_file=None, no_space=False):
        if type(configuration_file) is list:
            configuration_file = configuration_file[0]

        try:
            configuration = EnvAliasConfig(config_root=NAME).load_config(
                configuration_file=configuration_file,
                return_config=True
            )
            for config_k, config_v in configuration.items():
                env_name = config_k
                if 'name' in config_v.keys():
                    env_name = config_v['name']
                output_prefix = ' '
                if no_space is True:
                    output_prefix = ''
                value = self.obtain_value(config_k, config_v)
                if value is not None:
                    output = '{}export "{}"="{}"'.format(output_prefix, env_name, value)
                    logger.debug(output)
                    print(output)
                else:
                    logger.debug('env "{}" has no assignment'.format(env_name))

        except EnvAliasException as e:
            logger.error(e)

    def obtain_value(self, config_key, config):

        selector = None
        if 'selector' in config.keys():
            selector = config['selector']

        content_type = None
        if 'value' in config.keys():
            return config['value']
        elif 'source' in config.keys() and config['source'][0:4] == 'http':
            content, content_type = EnvAliasContent.remote(config['source'])
        elif 'source' in config.keys():
            content, content_type = EnvAliasContent.local(config['source'])
        elif 'exec' in config.keys():
            content, content_type = EnvAliasContent.exec(config['exec'])
            if 'selector' in config.keys() and selector is None:
                selector = 'none'
        else:
            raise EnvAliasException('Configuration of env-alias item "{}" is malformed'.format(config_key))

        parser = 'text'
        if 'parser' in config.keys():
            parser = config['parser']
        elif content_type is not None:
            parser = content_type

        if parser == 'ini':
            return EnvAliasSelector.ini_content(content, selector)
        elif parser == 'json':
            return EnvAliasSelector.json_content(content, selector)
        elif parser in ['yaml', 'yml']:
            return EnvAliasSelector.yaml_content(content, selector)

        return EnvAliasSelector.text_content(content, selector)
