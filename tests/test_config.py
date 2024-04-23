import os

import pytest

from config import get_env_bool, get_env_str


@pytest.fixture(autouse=True)
def set_up_env_vars():
    # Set up environment
    os.environ["CS_URL"] = "https://example.com"
    os.environ["TIMEZONE"] = "UTC"
    os.environ["TELEGRAM_API_TOKEN"] = "your_telegram_api_token"

    os.environ["SKIP_UPDATES"] = "true"
    os.environ["DATABASE"] = "false"


# TODO: make fixture to loadEnv and make a lot of tests
def test_loadEnv():
    # loadEnv()
    assert os.getenv("CS_URL") == "https://example.com"
    assert os.getenv("TIMEZONE") == "UTC"
    assert os.getenv("TELEGRAM_API_TOKEN") == "your_telegram_api_token"
    assert os.getenv("SKIP_UPDATES") == "true"


def test_getEnvBool():
    # Valid boolean strings
    assert get_env_bool("SKIP_UPDATES") is True
    assert get_env_bool("DATABASE") is False

    # Invalid cases
    assert get_env_bool("NON_EXISTING_ENV_VAR") is None
    assert get_env_bool("CS_URL") is None


def test_getStrOrNone():
    # Valid cases
    assert get_env_str("CS_URL") == "https://example.com"
    assert get_env_str("TIMEZONE") == "UTC"
    assert get_env_str("TELEGRAM_API_TOKEN") == "your_telegram_api_token"

    # Invalid cases
    assert get_env_str("NON_EXISTING_ENV_VAR") is None
