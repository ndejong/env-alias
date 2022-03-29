import time
import logging

__logger_default_format__ = "%(asctime)s - %(levelname)s - %(message)s"
__logger_default_dateformat__ = "%Y-%m-%dT%H:%M:%S%z"


class LoggerException(Exception):
    pass


class Logger:

    name = None
    logging = None
    default_level = "info"

    def __init__(self, name):
        self.name = name
        self.logging = logging.getLogger(self.name)

    def setup(self, level=None, fmt=__logger_default_format__, datefmt=__logger_default_dateformat__):

        logger_init = logging.getLogger(self.name)
        stream_handler = logging.StreamHandler()

        if level is not None:
            log_level = level.upper()
        else:
            log_level = self.default_level.upper()

        if log_level == "CRITICAL":
            logger_init.setLevel(logging.CRITICAL)
            stream_handler.setLevel(logging.CRITICAL)
        elif log_level == "ERROR":
            logger_init.setLevel(logging.ERROR)
            stream_handler.setLevel(logging.ERROR)
        elif log_level in ("WARNING", "WARN"):
            logger_init.setLevel(logging.WARNING)
            stream_handler.setLevel(logging.WARNING)
        elif log_level == "INFO":
            logger_init.setLevel(logging.INFO)
            stream_handler.setLevel(logging.INFO)
        elif log_level == "DEBUG":
            logger_init.setLevel(logging.DEBUG)
            stream_handler.setLevel(logging.DEBUG)
        else:
            raise LoggerException("unknown logger level value", log_level)

        logging.Formatter.converter = time.localtime
        stream_handler.setFormatter(LoggerColorFormatter(fmt=fmt, datefmt=datefmt))
        logger_init.addHandler(stream_handler)

        self.logging = logger_init
        return self.logging


class LoggerColorFormatter(logging.Formatter):

    color_line = "\x1b[90m"  # grey
    color_reset = "\x1b[0m"  # reset

    def __init__(self, **kwargs):
        if "fmt" in kwargs:
            kwargs["fmt"] = "{}{}{}".format(self.color_line, kwargs["fmt"], self.color_reset)
        logging.Formatter.__init__(self, **kwargs)

    def format(self, record):

        levelname = record.levelname.upper()

        if levelname == "CRITICAL":
            color_code = "\x1b[41m"  # white-on-red
        elif levelname == "ERROR":
            color_code = "\x1b[31m"  # red
        elif levelname in ("WARNING", "WARN"):
            color_code = "\x1b[33m"  # yellow
        elif levelname == "INFO":
            color_code = "\x1b[36m"  # cyan
        elif levelname == "DEBUG":
            color_code = "\x1b[37m"  # white
        else:
            color_code = "\x1b[90m"  # grey

        record.levelname = "{}{}{}{}".format(color_code, levelname, self.color_reset, self.color_line)
        return logging.Formatter.format(self, record)
