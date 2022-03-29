import sys
from env_alias import __env_alias_generator__


class EnvAlias:
    def main(self):
        args = sys.argv[1:]
        if len(args) < 2 or len(args) > 3:
            print("Usage: env-alias <alias> [-d] <config.yml>")
        else:
            print('alias "{}"="source <({} {})"'.format(args[0], __env_alias_generator__, " ".join(args[1:])))
