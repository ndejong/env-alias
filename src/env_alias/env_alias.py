import sys
from env_alias import __title__
from env_alias import __version__
from env_alias import __env_alias_generator__


class EnvAlias:
    def main(self):
        args = sys.argv[1:]
        if "--version" in args:
            print(f"{__title__} v{__version__}")
        elif len(args) < 2 or len(args) > 3:
            print("Usage: env-alias <alias> [-d] <config.yml>")
        else:
            print('alias "{}"="source <({} {})"'.format(args[0], __env_alias_generator__, " ".join(args[1:])))
