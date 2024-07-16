from typing import Any, List, Union

from . import LOGGER_LEVEL, LOGGER_NAME
from .lib.logger import logger_get

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


class EnvAliasBaseException(Exception):
    def __init__(self, *args: Union[str, List[Any]], **kwargs: Any) -> None:
        log_message = " ".join([str(x) for x in args]).strip()
        if log_message:
            logger.error(f"{log_message}")
        if "detail" in kwargs and LOGGER_LEVEL == "debug":
            logger.error(f"{kwargs['detail']}".strip())
        super().__init__(*args)


class EnvAliasException(EnvAliasBaseException):
    pass
