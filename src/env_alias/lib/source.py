import base64
import getpass
import hashlib
import os
import random
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.request
from pathlib import Path
from typing import Union

from .. import LOGGER_LEVEL, LOGGER_NAME, __title__, __version__
from ..exceptions import EnvAliasException
from ..lib.logger import logger_get
from ..models.sourced_content import SourcedContent

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


_SALT_SHAKE = "env-alias-sha256-salt"  # NB: not required to be secret


class EnvAliasSource:
    @staticmethod
    def local(filename: Path) -> SourcedContent:
        logger.debug(f"EnvAliasContent.local(filename={str(filename)})")

        content_type = "text"
        if str(filename).lower().endswith(".ini"):
            content_type = "ini"
        elif str(filename).lower().endswith(".json"):
            content_type = "json"
        elif str(filename).lower().endswith((".yml", "yaml")):
            content_type = "yaml"

        logger.debug(f"EnvAliasContent.local(filename={str(filename)}) > {content_type=}")

        filename = Path(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise EnvAliasException(f"Unable to locate filename={str(filename)!r}")

        with open(filename, "r") as f:
            content = f.read()

        if not content:
            raise EnvAliasException(f"Empty content received from filename={str(filename)!r}")

        return SourcedContent(source=str(filename), source_method="local", content=content, content_type=content_type)

    @staticmethod
    def remote(url: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.remote({url=})")

        req = urllib.request.Request(url, headers={"User-Agent": f"{__title__.replace(' ', '')}/{__version__}"})

        with urllib.request.urlopen(req) as res:
            content = res.read().decode()
            info = res.info()

        content_type = "text"
        if "ini" in info["content-type"].lower():
            content_type = "ini"
        elif "json" in info["content-type"].lower():
            content_type = "json"
        elif "yaml" in info["content-type"].lower():
            content_type = "yaml"
        elif url.lower().endswith(".ini"):
            content_type = "ini"
        elif url.lower().endswith(".json"):
            content_type = "json"
        elif url.lower().endswith((".yml", "yaml")):
            content_type = "yaml"

        logger.debug(f"EnvAliasContent.remote({url!r}) > {content_type=}")

        if not content:
            raise EnvAliasException(f"Empty content received from {url=}")

        return SourcedContent(source=str(url), source_method="remote", content=content, content_type=content_type)

    @staticmethod
    def execute(command_line: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.execute(command_line={command_line!r})")

        sp = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()

        if sp.returncode != 0:
            stdout_return = " ".join(str(stdout.decode("utf8")).split("\n"))[:256].strip()
            if stdout_return:
                logger.error(f"EnvAliasSource.execute stdout: {stdout_return!r}")
            stderr_return = " ".join(str(stderr.decode("utf8")).split("\n"))[:256].strip()
            raise EnvAliasException(f"EnvAliasSource.execute stderr: {stderr_return!r}", detail=command_line)

        content = stdout.decode("utf8").rstrip("\n")
        return SourcedContent(source=command_line, source_method="execute", content=content, content_type="text")

    @staticmethod
    def stdin(prompt: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.stdin({prompt=})")
        print(prompt, end="", file=sys.stderr)
        content = input()
        return SourcedContent(source=prompt, source_method="stdin", content=content, content_type="text")

    @staticmethod
    def getpass(prompt: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.getpass({prompt=})")
        content = getpass.getpass(prompt=prompt)
        return SourcedContent(source=prompt, source_method="getpass", content=content, content_type="text")

    @staticmethod
    def keepass(filename: Path, password: str, selector: Union[str, None]) -> SourcedContent:
        logger.debug(f"EnvAliasSource.keepass(filename={str(filename)}, password=<password>, {selector=})")

        keepassxc_cli = shutil.which("keepassxc-cli")
        if not keepassxc_cli:
            raise EnvAliasException("Unable to locate required binary 'keepassxc-cli', is it installed?")

        filename = Path(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise EnvAliasException(f"Unable to locate file {str(filename)!r}")

        if not selector or len(selector.split(":")) != 2:
            raise EnvAliasException(
                "Malformed keepass selector; must provide keepass-path to entry -and- "
                "the attribute name using a ':' separator in between."
            )

        keepass_path, keepass_attribute = selector.split(":")

        random_envvar = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(16))
        os.environ[random_envvar] = password
        command_line = (
            f' printf "${"{" + random_envvar + "}"}" | "{keepassxc_cli}" show '
            f'--quiet --show-protected --attributes "{keepass_attribute}" "{str(filename)}" "{keepass_path}"'
        )

        execute_content = EnvAliasSource.execute(command_line)
        os.unsetenv(random_envvar)

        return SourcedContent(
            source=str(filename), source_method="keepass", content=execute_content.content, content_type="text"
        )

    @staticmethod
    def ansible_vault(filename: Path, password: str) -> SourcedContent:
        logger.debug(f"EnvAliasSource.ansible_vault(filename={str(filename)}, password=<password>)")

        ansible_vault = shutil.which("ansible-vault")
        if not ansible_vault:
            raise EnvAliasException("Unable to locate required binary 'ansible-vault', is it installed?")

        filename = Path(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise EnvAliasException(f"Unable to locate file {str(filename)!r}")

        vault_password_file = EnvAliasSource.ansible_vault_password_file(password=password)

        os.environ[vault_password_file.source] = password
        os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = vault_password_file.content
        command_line = f' ansible-vault decrypt --output - "{filename}"'

        execute_content = EnvAliasSource.execute(command_line)
        os.unsetenv(vault_password_file.source)
        os.unlink(vault_password_file.content)

        return SourcedContent(
            source=str(filename), source_method="ansible_vault", content=execute_content.content, content_type="yaml"
        )

    @staticmethod
    def ansible_vault_password_file(password: str) -> SourcedContent:
        logger.debug("EnvAliasSource.ansible_vault_password_file(password=<password>)")

        password_shake_2rounds = EnvAliasSource.sha256_shaker(value=password, rounds=2)  # produces a consistent value
        envvar_name = "E" + password_shake_2rounds.upper()[0:11]

        ansible_vault_password_script = textwrap.dedent(
            f"""
            #!/bin/sh
            echo "${'{' + envvar_name + '}'}"
        """
        ).strip()

        password_shake_4rounds = EnvAliasSource.sha256_shaker(value=password, rounds=4)  # produces a consistent value
        vault_password_file = os.path.join(tempfile.gettempdir(), password_shake_4rounds.lower()[0:12])

        if not os.path.isfile(vault_password_file):
            with open(vault_password_file, "w") as f:
                f.write(ansible_vault_password_script)
            os.chmod(vault_password_file, 0o755)

        return SourcedContent(
            source=envvar_name,
            source_method="ansible_vault_password_file",
            content=vault_password_file,
            content_type="text",
        )

    @staticmethod
    def sha256_shaker(value: Union[str, bytes], rounds: int = 1, salt: str = _SALT_SHAKE, _round_count: int = 0) -> str:
        if _round_count == rounds:
            return base64.b64encode(value, altchars=b"az").decode()  # type: ignore[arg-type]

        h = hashlib.sha256()
        if isinstance(value, str):
            value = value.encode("utf8")
        h.update(salt.encode() + value)

        return EnvAliasSource.sha256_shaker(value=h.digest(), rounds=rounds, _round_count=_round_count + 1)
