import base64
import contextlib
import getpass
import hashlib
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from .. import LOGGER_LEVEL, LOGGER_NAME, __title__, __version__
from ..exceptions import EnvAliasException
from ..lib.logger import logger_get
from ..models.constants import ContentType, SourceMethod
from ..models.envalias_definition import EnvAliasDefinition
from ..models.sourced_content import SourcedContent

logger = logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)


_SALT_SHAKE = "env-alias-sha256-salt"  # NB: not required to be secret
_REMOTE_TIMEOUT_SECONDS = 30
_REMOTE_MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB limit

# Secrets registry: populated by the generator so source strategies can redact
# sensitive material in debug/error output.
_secrets_to_redact: dict[str, str] = {}


def _redact(text: str) -> str:
    """Replace known secret values in *text* with <redacted>."""
    redacted = text
    for value in _secrets_to_redact.values():
        if value and len(value) > 2:
            redacted = redacted.replace(value, "<redacted>")
    return redacted


# Extension to content-type mapping
_CONTENT_TYPE_EXTENSIONS: dict[str, ContentType] = {
    ".ini": ContentType.INI,
    ".json": ContentType.JSON,
    ".yml": ContentType.YAML,
    ".yaml": ContentType.YAML,
}


def _sniff_content_type(name: str, mime: str | None = None) -> ContentType:
    """Determine content type from MIME type or file extension."""
    if mime:
        mime_lower = mime.lower()
        if "ini" in mime_lower:
            return ContentType.INI
        if "json" in mime_lower:
            return ContentType.JSON
        if "yaml" in mime_lower:
            return ContentType.YAML

    name_lower = name.lower()
    for ext, content_type in _CONTENT_TYPE_EXTENSIONS.items():
        if name_lower.endswith(ext):
            return content_type

    return ContentType.TEXT


class EnvAliasSource:
    @staticmethod
    def local(filename: Path) -> SourcedContent:
        logger.debug(f"EnvAliasContent.local(filename={str(filename)})")

        content_type = _sniff_content_type(str(filename))

        logger.debug(f"EnvAliasContent.local(filename={str(filename)}) > {content_type=}")

        filename = Path(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise EnvAliasException(f"Unable to locate filename={str(filename)!r}")

        with open(filename) as f:
            content = f.read()

        if not content:
            raise EnvAliasException(f"Empty content received from filename={str(filename)!r}")

        return SourcedContent(
            source=str(filename), source_method=SourceMethod.LOCAL, content=content, content_type=content_type
        )

    @staticmethod
    def remote(url: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.remote({url=})")

        def _validate_scheme(u: str) -> None:
            if not u.startswith(("http://", "https://")):
                raise EnvAliasException(f"Rejected URL with disallowed scheme: {u!r}")

        _validate_scheme(url)

        req = urllib.request.Request(url, headers={"User-Agent": f"{__title__.replace(' ', '')}/{__version__}"})

        with urllib.request.urlopen(req, timeout=_REMOTE_TIMEOUT_SECONDS) as res:
            _validate_scheme(res.url)
            content = res.read(_REMOTE_MAX_RESPONSE_BYTES + 1)
            if len(content) > _REMOTE_MAX_RESPONSE_BYTES:
                raise EnvAliasException(f"Response from {url!r} exceeds {_REMOTE_MAX_RESPONSE_BYTES} byte limit")
            content = content.decode()
            info = res.info()

        content_type = _sniff_content_type(url, info.get("content-type"))

        logger.debug(f"EnvAliasContent.remote({url!r}) > {content_type=}")

        if not content:
            raise EnvAliasException(f"Empty content received from {url=}")

        return SourcedContent(
            source=str(url), source_method=SourceMethod.REMOTE, content=content, content_type=content_type
        )

    @staticmethod
    def execute(command_line: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.execute(command_line={_redact(command_line)!r})")

        sp = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()

        if sp.returncode != 0:
            stdout_return = " ".join(str(stdout.decode("utf8")).split("\n"))[:256].strip()
            if stdout_return:
                logger.error(f"EnvAliasSource.execute stdout: {stdout_return!r}")
            stderr_return = " ".join(str(stderr.decode("utf8")).split("\n"))[:256].strip()
            raise EnvAliasException(f"EnvAliasSource.execute stderr: {stderr_return!r}", detail=_redact(command_line))

        content = stdout.decode("utf8").rstrip("\n")
        return SourcedContent(
            source=command_line, source_method=SourceMethod.EXECUTE, content=content, content_type=ContentType.TEXT
        )

    @staticmethod
    def stdin(prompt: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.stdin({prompt=})")
        print(prompt, end="", file=sys.stderr)
        content = input()
        return SourcedContent(
            source=prompt, source_method=SourceMethod.STDIN, content=content, content_type=ContentType.TEXT
        )

    @staticmethod
    def getpass(prompt: str) -> SourcedContent:
        logger.debug(f"EnvAliasContent.getpass({prompt=})")
        content = getpass.getpass(prompt=prompt)
        return SourcedContent(
            source=prompt, source_method=SourceMethod.GETPASS, content=content, content_type=ContentType.TEXT
        )

    @staticmethod
    def keepass(filename: Path, password: str, selector: str | None) -> SourcedContent:
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

        # P1-2: build an argv list (no shell=True) and deliver the password via
        # stdin, instead of interpolating selector/source values into a shell
        # string. This removes the keepass shell-injection surface and keeps the
        # password off the command line and out of the child environment
        # entirely (it never touches os.environ, so there is nothing to clean up
        # on the success or failure path — P1-1 parity is trivially satisfied).
        command = [
            keepassxc_cli,
            "show",
            "--quiet",
            "--show-protected",
            "--attributes",
            keepass_attribute,
            str(filename),
            keepass_path,
        ]
        logger.debug(f"EnvAliasSource.keepass(command={_redact(' '.join(command))!r})")

        returncode, stdout, stderr = EnvAliasSource._keepass_run(command=command, password=password)

        if returncode != 0:
            stderr_return = " ".join(str(stderr.decode("utf8")).split("\n"))[:256].strip()
            raise EnvAliasException(
                f"EnvAliasSource.keepass stderr: {_redact(stderr_return)!r}",
                detail=_redact(" ".join(command)),
            )

        content = stdout.decode("utf8").rstrip("\n")
        return SourcedContent(
            source=str(filename),
            source_method=SourceMethod.KEEPASS,
            content=content,
            content_type=ContentType.TEXT,
        )

    @staticmethod
    def _keepass_run(command: list[str], password: str) -> tuple[int, bytes, bytes]:
        """Run a keepassxc-cli command, feeding the password via stdin.

        Split out so tests can stub the subprocess without a real database.
        Returns ``(returncode, stdout, stderr)``.
        """
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(input=password.encode("utf8"))
        return proc.returncode, stdout, stderr

    @staticmethod
    def ansible_vault(filename: Path, password: str) -> SourcedContent:
        logger.debug(f"EnvAliasSource.ansible_vault(filename={str(filename)}, password=<password>)")

        ansible_vault = shutil.which("ansible-vault")
        if not ansible_vault:
            raise EnvAliasException("Unable to locate required binary 'ansible-vault', is it installed?")

        filename = Path(os.path.expanduser(filename))
        if not os.path.isfile(filename):
            raise EnvAliasException(f"Unable to locate file {str(filename)!r}")

        # P1-5: Use an ephemeral random path for the scratch helper script
        # instead of the deterministic path from ansible_vault_password_file().
        # The deterministic path belongs to the `password_file` strategy which
        # must outlive this process; this method only needs a scratch file for
        # the duration of the decrypt command.
        random_envvar = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(16))
        os.environ[random_envvar] = password

        # Create an ephemeral password file at a random temp path
        fd, ephemeral_path = tempfile.mkstemp(prefix="env-alias-vault-")
        os.close(fd)
        script_content = textwrap.dedent(f"""
            #!/bin/sh
            echo "${"{" + random_envvar + "}"}"
        """).strip()
        try:
            with open(ephemeral_path, "w") as f:
                f.write(script_content)
            os.chmod(ephemeral_path, 0o700)
        except Exception:
            os.unlink(ephemeral_path)
            raise

        os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = ephemeral_path
        command_line = f' ansible-vault decrypt --output - "{filename}"'

        try:
            execute_content = EnvAliasSource.execute(command_line)
        finally:
            # os.environ.pop (not os.unsetenv) clears both the real environ
            # and the Python mapping (P1-1a). The try/finally ensures the
            # password env var, ANSIBLE_VAULT_PASSWORD_FILE, and the temp
            # script are all cleaned up even when execute raises — the
            # expected path for a wrong password (P1-1b).
            os.environ.pop(random_envvar, None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)
            with contextlib.suppress(OSError):
                os.unlink(ephemeral_path)

        return SourcedContent(
            source=str(filename),
            source_method=SourceMethod.ANSIBLE_VAULT,
            content=execute_content.content,
            content_type=ContentType.YAML,
        )

    @staticmethod
    def ansible_vault_password_file(password: str) -> SourcedContent:
        logger.debug("EnvAliasSource.ansible_vault_password_file(password=<password>)")

        password_shake_2rounds = EnvAliasSource.sha256_shaker(value=password, rounds=2)  # produces a consistent value
        # Ensure env-var name starts with a letter (required by POSIX). The hash
        # output contains digits, so map a leading digit to a letter by adding
        # the ASCII offset between '0' and 'A'.
        h = password_shake_2rounds.upper()[:11]
        envvar_name = chr(ord(h[0]) + 17) + h[1:] if h[0].isdigit() else h

        ansible_vault_password_script = textwrap.dedent(
            f"""
            #!/bin/sh
            echo "${"{" + envvar_name + "}"}"
        """
        ).strip()

        password_shake_4rounds = EnvAliasSource.sha256_shaker(value=password, rounds=4)  # produces a consistent value
        vault_password_file = os.path.join(tempfile.gettempdir(), password_shake_4rounds.lower()[0:12])

        if not os.path.isfile(vault_password_file):
            with open(vault_password_file, "w") as f:
                f.write(ansible_vault_password_script)
            os.chmod(vault_password_file, 0o700)

        return SourcedContent(
            source=envvar_name,
            source_method=SourceMethod.ANSIBLE_VAULT_PASSWORD_FILE,
            content=vault_password_file,
            content_type=ContentType.TEXT,
        )

    @staticmethod
    def sha256_shaker(value: str | bytes, rounds: int = 1, salt: str = _SALT_SHAKE, _round_count: int = 0) -> str:
        if _round_count == rounds:
            return base64.b64encode(value, altchars=b"az").decode()  # type: ignore[arg-type]

        h = hashlib.sha256()
        if isinstance(value, str):
            value = value.encode("utf8")
        h.update(salt.encode() + value)

        return EnvAliasSource.sha256_shaker(value=h.digest(), rounds=rounds, _round_count=_round_count + 1)


class SourceStrategy(NamedTuple):
    name: str
    matches: Callable[[EnvAliasDefinition], bool]
    fetch: Callable[[EnvAliasDefinition], SourcedContent]


SOURCE_STRATEGIES: list[SourceStrategy] = [
    SourceStrategy(
        name="remote",
        matches=lambda d: bool(d.source and d.source.startswith("http")),
        fetch=lambda d: EnvAliasSource.remote(url=d.source),  # type: ignore[arg-type]
    ),
    SourceStrategy(
        name="stdin",
        matches=lambda d: bool(d.source and d.source == "<stdin>"),
        fetch=lambda d: EnvAliasSource.stdin(prompt=f"Enter {d.name!r} value using <stdin>: "),
    ),
    SourceStrategy(
        name="getpass",
        matches=lambda d: bool(d.source and d.source == "<getpass>"),
        fetch=lambda d: EnvAliasSource.getpass(prompt=f"Enter {d.name!r} value using <getpass>: "),
    ),
    SourceStrategy(
        name="keepass",
        matches=lambda d: bool(d.source and d.keepass_password),
        fetch=lambda d: EnvAliasSource.keepass(
            filename=Path(d.source),
            password=d.keepass_password,
            selector=d.selector,  # type: ignore[arg-type]
        ),
    ),
    SourceStrategy(
        name="ansible_vault",
        matches=lambda d: bool(d.source and d.ansible_vault_password),
        fetch=lambda d: EnvAliasSource.ansible_vault(
            filename=Path(d.source),
            password=d.ansible_vault_password,  # type: ignore[arg-type]
        ),
    ),
    SourceStrategy(
        name="ansible_vault_password_file",
        matches=lambda d: bool(d.ansible_vault_password and d.ansible_vault_password_file),
        fetch=lambda d: EnvAliasSource.ansible_vault_password_file(  # type: ignore[arg-type]
            password=d.ansible_vault_password
        ),
    ),
    SourceStrategy(
        name="local",
        matches=lambda d: bool(d.source),
        fetch=lambda d: EnvAliasSource.local(filename=Path(d.source)),  # type: ignore[arg-type]
    ),
    SourceStrategy(
        name="exec",
        matches=lambda d: bool(d.exec_),
        fetch=lambda d: EnvAliasSource.execute(command_line=d.exec_),  # type: ignore[arg-type]
    ),
]
