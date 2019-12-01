
import os
import tempfile
import pytest
from unittest.mock import patch
import EnvAlias


def test_name_exist():
    ea = EnvAlias
    assert ea.NAME is not None


def test_version_exist():
    ea = EnvAlias
    assert ea.VERSION is not None
