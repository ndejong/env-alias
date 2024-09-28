#
# Copyright [2020] Nicholas de Jong (https://www.nicholasdejong.com)
#

from os import getenv
from sys import argv

__title__ = "Env Alias"
__version__ = "0.5.3"

LOGGER_LEVEL = "info"
if "--debug" in argv or getenv("ENVALIAS_DEBUG", "").lower().startswith(("true", "yes", "enable", "on")):
    LOGGER_LEVEL = "debug"

LOGGER_NAME = "env-alias"
DEFINITIONS_ROOT = "env-alias"
