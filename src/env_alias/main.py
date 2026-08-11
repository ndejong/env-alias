import argparse
import os
import re
import sys
from pathlib import Path

from . import LOGGER_LEVEL, LOGGER_NAME, __title__, __version__
from .exceptions import EnvAliasException
from .lib.logger import logger_get, logger_setlevel

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)

# Alias names (unlike environment variable names) may contain hyphens, e.g.
# ``env-awesome-vars``. Hyphens are safe inside the double-quoted alias-name
# in the emitted ``alias`` statement — the P0-2 injection hardening guarded
# against ``$`\\`` characters, not ``-``.
_ALIAS_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")


def entrypoint() -> None:
    parser = argparse.ArgumentParser(
        description=f"{__title__} v{__version__}",
        epilog="Usage: env-alias [<alias>] [--debug] <definitions.[yml|yaml]>",
        add_help=False,
    )
    parser.add_argument("--version", action="version", version=f"{__title__} v{__version__}")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--generator", action="store_true")
    parser.add_argument("args", nargs="*")

    try:
        args = parser.parse_args()

        if args.debug:
            logger_setlevel(LOGGER_NAME, "debug")

        if args.generator:
            if not args.args:
                usage_help(exit_code=0)
            from env_alias.lib.generator import EnvAliasGenerator

            EnvAliasGenerator(config_file=[Path(f) for f in args.args]).generate()
            return

        if not args.args:
            usage_help(exit_code=0)
            return

        # Process positionals for alias mode. The result is a list of
        # (alias_name, filename) pairs, one entry per alias to emit.
        if len(args.args) == 1:
            # Single arg: derive alias name from the filename basename.
            entries = [
                (
                    os.path.splitext(os.path.basename(args.args[0]))[0],
                    args.args[0],
                )
            ]
        elif len(args.args) >= 2:
            if os.path.isfile(args.args[0]):
                # First arg is a file: ALL args are definition files. Emit one
                # alias per file, each name inferred from its own basename, so a
                # single invocation defines N independent lazily-loaded aliases.
                entries = [(os.path.splitext(os.path.basename(f))[0], f) for f in args.args]
            else:
                # First arg is an explicit alias name — only a single definition
                # file may follow; with multiple files the intent is ambiguous.
                alias_name = args.args[0]
                trailing = args.args[1:]
                if len(trailing) > 1:
                    raise EnvAliasException(
                        f"An explicit alias name may be followed by only one definition file, got {len(trailing)}."
                    )
                entries = [(alias_name, trailing[0])]
        else:
            usage_help(exit_code=0)
            return

        # Validate every inferred/explicit alias name up front so that a single
        # bad name never yields partial alias output on stdout.
        for alias_name, _ in entries:
            if not _ALIAS_NAME_RE.fullmatch(alias_name):
                raise EnvAliasException(f"Invalid alias name {alias_name!r}: must match ^[A-Za-z_][A-Za-z0-9_-]*$")

        # Emit one alias per entry. Each RHS runs the generator against that
        # entry's single definition file only, preserving per-alias lazy loading.
        generator_cmd = "env-alias"
        if args.debug:
            generator_cmd += " --debug"
        for alias_name, filename in entries:
            quoted_file = "'" + filename.replace("'", "'\\''") + "'"
            rhs = f"source <({generator_cmd} --generator {quoted_file})"

            rhs_dq = rhs.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
            alias_command = f'alias "{alias_name}"="{rhs_dq}"'
            logger.debug(alias_command)
            print(alias_command)

    except EnvAliasException:
        print("Exiting", file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        print("Exiting", file=sys.stderr)
        exit(130)
    except SystemExit as e:
        if e.code == 0:
            return
        exit(e.code)


def usage_help(exit_code: int | None = None) -> None:
    print()
    print(f"{__title__} v{__version__}")
    print()
    print("Usage: env-alias [<alias>] [--debug] <definitions.[yml|yaml]>")
    print("Docs: https://threatpatrols.github.io/env-alias/")
    print()
    if exit_code is not None:
        exit(exit_code)
