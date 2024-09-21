import os
import sys
from pathlib import Path
from typing import List, Tuple, Union

from . import LOGGER_LEVEL, LOGGER_NAME, __title__, __version__
from .exceptions import EnvAliasException
from .lib.logger import logger_get

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


def entrypoint() -> None:
    args = sys.argv[1:]

    if "--version" in args:
        print(f"{__title__} v{__version__}")

    elif "--generator" in args:
        from env_alias.lib.generator import EnvAliasGenerator

        try:
            EnvAliasGenerator(config_file=Path(args[-1])).generate()
        except EnvAliasException:
            print("Exiting", file=sys.stderr)
            exit(0)
        except KeyboardInterrupt:
            print("Exiting", file=sys.stderr)
            exit(0)

    elif len(args) < 1 or len(args) > 3:
        usage_help(exit_code=0)

    else:
        alias_name, generator_args = handle_args(args)
        alias_command = f'alias "{alias_name}"="source <(env-alias --generator {generator_args})"'
        logger.debug(alias_command)
        print(alias_command)


def handle_args(args: List[str]) -> Tuple[str, str]:
    debug_switch = False
    if "--debug" in args:
        debug_switch = True
        del args[args.index("--debug")]

    if len(args) == 1:
        alias_name = os.path.splitext(os.path.basename(args[0]))[0]
        logger.debug(f"Alias name {alias_name!r} inferred from definitions file-name.")
        filename = args[0]
    else:
        alias_name = args[0]
        logger.debug(f"Alias name {alias_name!r} user provided.")
        filename = " ".join(args[1:])

    generator_args = f"{filename!r}"

    if debug_switch:
        generator_args = f"--debug {generator_args}"

    return alias_name, generator_args


def usage_help(exit_code: Union[int, None] = None) -> None:
    print()
    print(f"{__title__} v{__version__}")
    print()
    print("Usage: env-alias [<alias>] [--debug] <definitions.[yml|yaml]>")
    print("Docs: https://env-alias.readthedocs.io")
    print()
    if exit_code:
        exit(exit_code)
