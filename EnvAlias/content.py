
import os
import urllib.request
import subprocess

from . import NAME
from . import VERSION


class EnvAliasContentException(Exception):
    pass


class EnvAliasContent:

    @staticmethod
    def local(filename):

        content_type = 'text'
        if filename.lower()[-4:] in ['.ini']:
            content_type = 'ini'
        elif filename.lower()[-5:] in ['.json']:
            content_type = 'json'
        elif filename.lower()[-4:] in ['.yml', 'yaml']:
            content_type = 'yaml'

        filename = os.path.expanduser(filename)

        if not os.path.exists(filename):
            raise EnvAliasContentException('Unable to locate file required to load', filename)
        with open(filename, 'r') as f:
            return f.read(), content_type

    @staticmethod
    def remote(url):

        req = urllib.request.Request(
            url,
            headers={'User-Agent': '{}/{}'.format(NAME, VERSION)}
        )

        with urllib.request.urlopen(req) as res:
            content = res.read().decode()
            info = res.info()

        content_type = 'text'
        if 'ini' in info['content-type'].lower():
            content_type = 'ini'
        elif 'json' in info['content-type'].lower():
            content_type = 'json'
        elif 'yaml' in info['content-type'].lower():
            content_type = 'yaml'
        elif url.lower()[-4:] in ['.ini']:
            content_type = 'ini'
        elif url.lower()[-5:] in ['.json']:
            content_type = 'json'
        elif url.lower()[-4:] in ['.yml', 'yaml']:
            content_type = 'yaml'

        return content, content_type

    @staticmethod
    def exec(command_line):
        sp = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()
        if stderr:
            raise EnvAliasContentException(stderr.decode('utf8').rstrip('\n'))
        return stdout.decode('utf8').rstrip('\n'), None
