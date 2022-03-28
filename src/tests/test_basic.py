import env_alias


def test_name_exist():
    ea = env_alias
    assert ea.__title__ is not None


def test_version_exist():
    ea = env_alias
    assert ea.__version__ is not None
