import logging
from typing import Any

from . import LOGGER_NAME
from .lib.logger import logger_get

logger = logger_get(name=LOGGER_NAME, loglevel="info")


class EnvAliasBaseException(Exception):
    def __init__(self, *args: str | list[Any], **kwargs: Any) -> None:
        log_message = " ".join([str(x) for x in args]).strip()
        if log_message:
            logger.error(f"{log_message}")
        if "detail" in kwargs and logger.isEnabledFor(logging.DEBUG):
            logger.error(f"{kwargs['detail']}".strip())
        super().__init__(*args)


class EnvAliasException(EnvAliasBaseException):
    pass
