import sys
import argparse

from env_alias import __title__ as NAME
from env_alias import __version__ as VERSION
from env_alias import __logger_default_level__ as LOGGER_DEFAULT_LEVEL
from env_alias.exceptions import EnvAliasException


def env_alias():
    from env_alias.env_alias import EnvAlias

    try:
        EnvAlias().main()
    except EnvAliasException as e:
        __entrypoint_exception_handler(e)


def env_alias_generator():
    from env_alias.env_alias_generator import EnvAliasGenerator

    parser = argparse.ArgumentParser(
        description="{} v{}".format(NAME, VERSION),
        add_help=False,
        epilog="""
            Helper tool to create shell alias commands to easily set collections of environment variables, often with
            secrets, from a variety of sources and formats.  Typically this tool is invoked via an entry in
            `.bash_aliases` with an entry in the form
            `eval $(env-alias my-alias-name ~/path-to/my-alias-name-config-file.yml)` where this example would hence
            establish a shell alias for the command `my-alias-name` that then invokes this `env-alias-generator` with
            the configuration from `~/path-to/my-alias-name-config-file.yml`.  The result then is that the environment
            variables defined in the configuration are loaded into the current shell.  This provides an easy mechanism
            to manage sets of environment variables with values from encrypted or otherwise secured data-sources
            through one simple alias command and a configuration file that can safely be committed to source control
            without exposing secret values.
        """,
    )

    parser.add_argument(
        "config", metavar="<config-file>", type=str, nargs=1, help="An env-alias YAML style configuration file."
    )

    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="Debug logging output (default: False)."
    )

    if len(sys.argv) == 1:
        parser.print_help()
        print()
        exit(1)

    args = parser.parse_args()

    if args.debug:
        logger_level = "debug"
    else:
        logger_level = LOGGER_DEFAULT_LEVEL

    try:
        EnvAliasGenerator(logger_level=logger_level).main(configuration_file=args.config)
    except EnvAliasException as e:
        __entrypoint_exception_handler(e)


def __entrypoint_exception_handler(e):
    print("")
    print("{} v{}".format(NAME, VERSION))
    print("ERROR: ", end="")
    for err in iter(e.args):
        print(err)
    print("")
    exit(9)
