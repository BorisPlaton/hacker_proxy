import pytest

from configuration.settings import settings
from proxy.handlers import UserRequestHandler, HttpParser


@pytest.fixture
def proxy_settings():
    return settings['PROXY_SERVER']


@pytest.fixture
def request_handler():
    return UserRequestHandler()


@pytest.fixture
def http_parser():
    return HttpParser()


@pytest.fixture
def response_handler():
    return HttpParser()
