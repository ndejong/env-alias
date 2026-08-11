#
# Copyright [2020] Nicholas de Jong (https://www.nicholasdejong.com)
#

from os import getenv

__title__ = "Env Alias"
__version__ = "0.7.1"

LOGGER_LEVEL = "info"
if getenv("ENVALIAS_DEBUG", "").lower().startswith(("true", "yes", "enable", "on")):
    LOGGER_LEVEL = "debug"

LOGGER_NAME = "env-alias"
DEFINITIONS_ROOT = "env-alias"
