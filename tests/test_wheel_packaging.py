"""Verify the built wheel packages all subpackages.

Regression guard: the setuptools migration used an
explicit non-recursive package list, which produced a wheel containing only
the top-level ``env_alias`` package and silently dropped ``env_alias.lib``
and ``env_alias.models``. Any ``pip install`` from that wheel failed at
runtime with ``ModuleNotFoundError``.
"""

import shutil
import subprocess
import zipfile
from os import environ
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

REQUIRED_WHEEL_ENTRIES = [
    "env_alias/__init__.py",
    "env_alias/py.typed",
    "env_alias/exceptions.py",
    "env_alias/main.py",
    "env_alias/lib/__init__.py",
    "env_alias/lib/generator.py",
    "env_alias/lib/source.py",
    "env_alias/lib/selector.py",
    "env_alias/lib/definitions.py",
    "env_alias/lib/logger.py",
    "env_alias/models/__init__.py",
    "env_alias/models/envalias_definition.py",
    "env_alias/models/sourced_content.py",
]


def _uv() -> str:
    uv = shutil.which("uv")
    assert uv is not None, "uv executable not found on PATH"
    return uv


def _build_wheel(out_dir: Path) -> Path:
    """Build the wheel into ``out_dir`` and return its path.

    Uses ``uv build`` rather than ``pip wheel`` because the dev venv is
    uv-managed and has no pip. Keeps the build isolated from the host.
    """
    env = {
        "UV_PROJECT_ENVIRONMENT": str(Path.home() / ".local/venvs/env-alias"),
        "UV_CACHE_DIR": "/tmp/.uv-cache-env-alias",
        "UV_LINK_MODE": "copy",
        "PATH": environ["PATH"],
    }
    subprocess.run(
        [_uv(), "build", "--wheel", "-o", str(out_dir), "."],
        check=True,
        capture_output=True,
        env=env,
    )
    wheels = list(out_dir.glob("env_alias-*.whl"))
    assert len(wheels) == 1, f"expected exactly one wheel, got {wheels}"
    return wheels[0]


def test_wheel_contains_all_subpackages(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    names = zipfile.ZipFile(wheel).namelist()
    missing = [entry for entry in REQUIRED_WHEEL_ENTRIES if entry not in names]
    assert not missing, f"wheel missing required entries: {missing}\nwheel contents:\n  " + "\n  ".join(sorted(names))


def test_wheel_entrypoint_runs(tmp_path: Path) -> None:
    """Install the freshly built wheel into a throwaway venv and run the CLI.

    A ``--version``-only smoke test would miss the subpackage import gap; the
    generator run is what proves ``env_alias.lib`` and ``env_alias.models``
    import cleanly from an installed wheel.
    """
    wheel = _build_wheel(tmp_path)
    venv = tmp_path / "venv"
    uv = _uv()
    env = {
        "UV_CACHE_DIR": "/tmp/.uv-cache-env-alias",
        "UV_LINK_MODE": "copy",
        "PATH": environ["PATH"],
    }
    subprocess.run([uv, "venv", str(venv)], check=True, capture_output=True, env=env)
    subprocess.run(
        [uv, "pip", "install", "--python", str(venv / "bin" / "python"), str(wheel)],
        check=True,
        capture_output=True,
        env=env,
    )

    env_alias_bin = venv / "bin" / "env-alias"
    version = subprocess.run([str(env_alias_bin), "--version"], capture_output=True, text=True)
    assert version.returncode == 0, version.stderr
    assert version.stdout.strip()

    # Drive a real generator run: this is what proves env_alias.lib and
    # env_alias.models import cleanly from an installed wheel. ``--version``
    # alone only exercises the top-level package.
    data_file = tmp_path / "data.txt"
    data_file.write_text("hello-wheel\n")
    definitions_file = tmp_path / "def.yml"
    definitions_file.write_text(f"env-alias:\n  SMOKE:\n    source: {data_file}\n    selector: 1\n")
    gen = subprocess.run(
        [str(env_alias_bin), "--generator", str(definitions_file)],
        capture_output=True,
        text=True,
    )
    assert gen.returncode == 0, gen.stderr
    assert "export" in gen.stdout
    assert "SMOKE" in gen.stdout
