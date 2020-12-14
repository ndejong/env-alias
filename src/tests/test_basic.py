
<<<<<<< HEAD
=======
import os
import tempfile
import pytest
from unittest.mock import patch
>>>>>>> 18fafcd6b250d053d6f854f154623e33601fe2b9
import env_alias


def test_name_exist():
    ea = env_alias
    assert ea.__title__ is not None


def test_version_exist():
    ea = env_alias
    assert ea.__version__ is not None
