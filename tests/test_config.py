import os

import pytest

from config import getEnvBool, getStrOrNone


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
    assert getEnvBool("SKIP_UPDATES") is True
    assert getEnvBool("DATABASE") is False

    # Invalid cases
    assert getEnvBool("NON_EXISTING_ENV_VAR") is None
    assert getEnvBool("CS_URL") is None


def test_getStrOrNone():
    # Valid cases
    assert getStrOrNone("CS_URL") == "https://example.com"
    assert getStrOrNone("TIMEZONE") == "UTC"
    assert getStrOrNone("TELEGRAM_API_TOKEN") == "your_telegram_api_token"

    # Invalid cases
    assert getStrOrNone("NON_EXISTING_ENV_VAR") is None
