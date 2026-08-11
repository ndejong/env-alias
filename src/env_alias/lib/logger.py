import logging
from typing import Any

LOGGING_FORMAT = "%(asctime)s | %(levelname)s | __name__ | %(message)s"
LOGGING_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def logger_get(name: str, loglevel: str = "warning", logfile: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logging_level = __logger_level_int(loglevel)
    logger.setLevel(logging_level)

    logging_formatter = LoggingFormatterWrapper(
        fmt=LOGGING_FORMAT, datefmt=LOGGING_TIMESTAMP_FORMAT, name=name, colorize_levelname=True
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(logging_formatter)

    logger.addHandler(console_handler)

    try:
        if logfile:
            file_handler = logging.FileHandler(filename=logfile)
            file_handler.setLevel(logging_level)
            file_handler.setFormatter(logging_formatter)
            logger.addHandler(file_handler)
    except (FileNotFoundError, PermissionError) as e:
        raise PermissionError(f"Unable to write to logfile at: {logfile}") from e

    return logger


def logger_setlevel(name: str, loglevel: str) -> logging.Logger:
    logger = logger_get(name)
    logging_level = __logger_level_int(loglevel)

    logger.setLevel(logging_level)
    if isinstance(logger.handlers, list):
        for handler in logger.handlers:
            handler.setLevel(logging_level)

    return logger


def __logger_level_int(loglevel: str) -> int:
    logging_level = logging.getLevelName(loglevel.upper())
    try:
        int(logging_level)
    except ValueError:
        raise ValueError(f"Unknown loglevel requested: {loglevel}") from None

    return int(logging_level)


class LoggingFormatterWrapper(logging.Formatter):
    colorize_levelname: bool = False

    def __init__(self, **kwargs: Any) -> None:
        if "name" in kwargs:
            kwargs["fmt"] = kwargs.get("fmt", LOGGING_FORMAT).replace("__name__", kwargs["name"])
            del kwargs["name"]
        if "colorize_levelname" in kwargs:
            self.colorize_levelname = True
            del kwargs["colorize_levelname"]
        logging.Formatter.__init__(self, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        if self.colorize_levelname:
            return self.colorized_levelname_format(record)
        return logging.Formatter.format(self, record)

    def colorized_levelname_format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname.upper()

        if levelname == "CRITICAL":
            color_code = "\x1b[1;41m"  # white-on-red
        elif levelname == "ERROR":
            color_code = "\x1b[1;31m"  # red
        elif levelname in ("WARNING", "WARN"):
            color_code = "\x1b[1;33m"  # yellow
        elif levelname == "INFO":
            color_code = "\x1b[1;36m"  # cyan
        elif levelname == "DEBUG":
            color_code = "\x1b[1;37m"  # white
        else:
            color_code = None

        if color_code:
            color_reset = "\x1b[0m"  # reset
            record.levelname = f"{color_code}{record.levelname}{color_reset}"

        return logging.Formatter.format(self, record)
