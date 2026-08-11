import functools
import http.server
import json
import os
import threading
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def config_file(tmp_path: Path):
    """Fixture to create a temporary configuration file.

    Usage:
    def test_something(config_file, capsys):
        yaml = \"\"\"\n        VAR:\n            value: val\n        \"\"\"\n        f = config_file(yaml)\n        ...
    """

    def _create_config(yaml_content: str) -> Path:
        config = "env-alias:\n" + yaml_content
        f = tmp_path / "def.yml"
        f.write_text(config)
        return f

    return _create_config


@pytest.fixture
def http_file_server(tmp_path: Path):
    """Serve a small static file tree over a local HTTP server.

    Replaces live third-party URLs in remote-source tests so the test
    suite no longer depends on the network. Yields the base URL.
    """
    (tmp_path / "144disk.txt").write_text("line one\nline two\nline three\nline four\nline five\n")
    (tmp_path / "data.json").write_text(
        json.dumps(
            {
                "prefixes": [
                    {"ip_prefix": "0.0.0.0/0"},
                    {"ip_prefix": "1.1.1.1/32"},
                    {"ip_prefix": "2001:db8::/32"},
                ]
            }
        )
    )
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def mkdocs_nav() -> list[str]:
    """Return Markdown paths referenced by the MkDocs navigation only."""

    class MkDocsLoader(yaml.SafeLoader):
        pass

    def construct_unknown(loader, _tag_suffix, node):
        if isinstance(node, yaml.ScalarNode):
            return loader.construct_scalar(node)
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_mapping(node)

    MkDocsLoader.add_multi_constructor("", construct_unknown)

    def collect_paths(node: object) -> list[str]:
        if isinstance(node, str):
            return [node] if node.endswith(".md") else []
        if isinstance(node, list):
            return [path for entry in node for path in collect_paths(entry)]
        if isinstance(node, dict):
            return [path for entry in node.values() for path in collect_paths(entry)]
        return []

    mkdocs_path = Path(__file__).resolve().parent.parent / "docs" / "mkdocs.yml"
    config = yaml.load(mkdocs_path.read_text(), Loader=MkDocsLoader)
    return collect_paths(config["nav"])


@pytest.fixture(autouse=True)
def isolate_environ():
    old_environ = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_environ)
