import os
import sys

import tempfile
import random
import string

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "env_alias"))


def __rewrite_configuration_file(configuration_file, **kwargs):

    with open(configuration_file, "r") as f:
        config = f.read()

    for key, value in kwargs.items():
        config = config.replace("{" + key + "}", value)

    temp_configuration_file = os.path.join(
        tempfile.gettempdir(), "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    )

    with open(temp_configuration_file, "w") as f:
        f.write(config)

    return temp_configuration_file
