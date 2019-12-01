
import time
import logging

from . import NAME
from . import EnvAliasException


class ColoredLoggingFormatter(logging.Formatter):

    color_line = '\x1b[90m'  # grey
    color_reset = '\x1b[0m'  # reset

    def __init__(self, **kwargs):
        if 'fmt' in kwargs:
            kwargs['fmt'] = '{}{}{}'.format(self.color_line, kwargs['fmt'], self.color_reset)
        logging.Formatter.__init__(self, **kwargs)

    def format(self, record):

        levelname = record.levelname.upper()

        if levelname == 'CRITICAL':
            color_code = '\x1b[41m'  # white-on-red
        elif levelname == 'ERROR':
            color_code = '\x1b[31m'  # red
        elif levelname in ('WARNING', 'WARN'):
            color_code = '\x1b[33m'  # yellow
        elif levelname == 'INFO':
            color_code = '\x1b[36m'  # cyan
        elif levelname == 'DEBUG':
            color_code = '\x1b[37m'  # white
        else:
            color_code = '\x1b[90m'  # grey

        record.levelname = '{}{}{}'.format(color_code, levelname, self.color_line)

        return logging.Formatter.format(self, record)


class EnvAliasLogger:

    logger = None
    default_level = 'info'

    def __init__(self, level=None):

        if level is not None:
            log_level = level
        else:
            log_level = self.default_level

        logger_init = logging.getLogger(NAME)
        if logger_init.level > 0:
            self.logger = logger_init
            return

        logger_init.setLevel(logging.DEBUG)

        log_level = log_level.upper()
        stream_handler = logging.StreamHandler()

        if log_level == 'CRITICAL':
            stream_handler.setLevel(logging.CRITICAL)
        elif log_level == 'ERROR':
            stream_handler.setLevel(logging.ERROR)
        elif log_level in ('WARNING', 'WARN'):
            stream_handler.setLevel(logging.WARNING)
        elif log_level == 'INFO':
            stream_handler.setLevel(logging.INFO)
        elif log_level == 'DEBUG':
            stream_handler.setLevel(logging.DEBUG)
        elif log_level is not None:
            raise EnvAliasException('unknown loglevel value', log_level)
        else:
            stream_handler.setLevel(logging.NOTSET)

        formatter = ColoredLoggingFormatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y%m%dZ%H%M%S'
        )
        logging.Formatter.converter = time.gmtime

        stream_handler.setFormatter(formatter)
        logger_init.addHandler(stream_handler)

        self.logger = logger_init
