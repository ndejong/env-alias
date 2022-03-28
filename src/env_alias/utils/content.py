import os
import urllib.request
import subprocess

from env_alias import __title__ as NAME
from env_alias import __version__ as VERSION
from env_alias.utils import logger
from env_alias.exceptions import EnvAliasException


class EnvAliasContent:
    @staticmethod
    def local(filename):

        content_type = "text"
        if filename.lower()[-4:] in [".ini"]:
            content_type = "ini"
        elif filename.lower()[-5:] in [".json"]:
            content_type = "json"
        elif filename.lower()[-4:] in [".yml", "yaml"]:
            content_type = "yaml"

        filename = os.path.expanduser(filename)

        if not os.path.exists(filename):
            raise EnvAliasException("Unable to locate file required to load", filename)

        logger.debug("Config content from: {}".format(filename))
        with open(filename, "r") as f:
            content = f.read()

        logger.debug("Config classified as: {}".format(content_type))
        return content, content_type

    @staticmethod
    def remote(url):

        req = urllib.request.Request(url, headers={"User-Agent": "{}/{}".format(NAME, VERSION)})

        logger.debug("Config content from: {}".format(url))
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
        elif url.lower()[-4:] in [".ini"]:
            content_type = "ini"
        elif url.lower()[-5:] in [".json"]:
            content_type = "json"
        elif url.lower()[-4:] in [".yml", "yaml"]:
            content_type = "yaml"

        logger.debug("Config classified as: {}".format(content_type))
        return content, content_type

    @staticmethod
    def execute(command_line):

        logger.debug("Config content from: {}".format(command_line))
        sp = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()
        if stderr:
            raise EnvAliasException(stderr.decode("utf8").rstrip("\n"))
        return stdout.decode("utf8").rstrip("\n"), None
