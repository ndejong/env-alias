import argparse
import glob
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
_ALIAS_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_DEF_FILE_RE = re.compile(r"^[A-Za-z0-9_-]+\.ya?ml$", re.IGNORECASE)
_DEF_GLOB_RE = re.compile(r"^.*\.ya?ml$", re.IGNORECASE)


def _resolve_definition_files(arg: str) -> list[str]:
    """Resolve a positional argument to one or more definition filenames.

    Globs (*, ?) are expanded; an empty match logs a warning and returns [].
    Static filenames are validated syntactically (must match _DEF_FILE_RE)
    without touching the filesystem.
    """
    clean_path = arg.rstrip("/\\")
    basename = os.path.basename(clean_path)
    if not basename:
        raise EnvAliasException(f"Definition file path {arg!r} is invalid: must be a YAML file, not a directory.")

    if glob.has_magic(arg):
        if not _DEF_GLOB_RE.fullmatch(basename):
            raise EnvAliasException(f"Definition glob pattern {arg!r} must end with .yml or .yaml")
        matches = sorted(glob.glob(os.path.expanduser(arg)))
        if not matches:
            logger.warning(f"No definition files matched glob pattern: {arg}")
            return []
        for f in matches:
            fb = os.path.basename(f)
            if not _DEF_FILE_RE.fullmatch(fb):
                raise EnvAliasException(f"Matched definition filename {fb!r} must match ^[A-Za-z0-9_-]+\\.ya?ml$")
        return matches

    if not _DEF_FILE_RE.fullmatch(basename):
        raise EnvAliasException(f"Definition filename {basename!r} must match ^[A-Za-z0-9_-]+\\.ya?ml$")

    return [arg]


def _is_definition_arg(arg: str) -> bool:
    """Return True if arg looks like a definition file or glob rather than an alias name."""
    clean_path = arg.rstrip("/\\")
    basename = os.path.basename(clean_path)
    return bool(glob.has_magic(arg) or _DEF_FILE_RE.fullmatch(basename) or basename.lower().endswith((".yml", ".yaml")))


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
        entries: list[tuple[str, str]] = []

        if len(args.args) == 1:
            files = _resolve_definition_files(args.args[0])
            if not files:
                return
            entries = [(os.path.splitext(os.path.basename(f))[0], f) for f in files]

        elif len(args.args) == 2:
            arg0, arg1 = args.args[0], args.args[1]
            if _is_definition_arg(arg0):
                # Multi-file mode: both args are definition files / patterns
                for arg in args.args:
                    for f in _resolve_definition_files(arg):
                        entries.append((os.path.splitext(os.path.basename(f))[0], f))
            else:
                # First arg is explicit alias name
                alias_name = arg0
                if not _ALIAS_NAME_RE.fullmatch(alias_name):
                    raise EnvAliasException(f"Invalid alias name {alias_name!r}: must match ^[A-Za-z_][A-Za-z0-9_-]*$")
                files = _resolve_definition_files(arg1)
                if not files:
                    return
                if len(files) > 1:
                    raise EnvAliasException(
                        f"An explicit alias name may be followed by only one definition file, got {len(files)}."
                    )
                entries = [(alias_name, files[0])]

        elif len(args.args) >= 3:
            arg0 = args.args[0]
            if not _is_definition_arg(arg0) and _ALIAS_NAME_RE.fullmatch(arg0):
                trailing = args.args[1:]
                raise EnvAliasException(
                    f"An explicit alias name may be followed by only one definition file, got {len(trailing)}."
                )
            for arg in args.args:
                for f in _resolve_definition_files(arg):
                    entries.append((os.path.splitext(os.path.basename(f))[0], f))
        else:
            usage_help(exit_code=0)
            return

        if not entries:
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
