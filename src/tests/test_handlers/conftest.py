import pytest

from configuration.settings import settings


@pytest.fixture
def proxy_settings():
    return settings['PROXY_SERVER']
