import pytest

from configuration.settings import settings
from proxy.handlers import UserRequestHandler, HttpParser, ServerResponseHandler


@pytest.fixture
def project_settings():
    return settings


@pytest.fixture
def proxy_settings():
    return settings.proxy_settings


@pytest.fixture
def request_handler():
    return UserRequestHandler()


@pytest.fixture
def http_parser():
    return HttpParser()


@pytest.fixture
def response_handler():
    return ServerResponseHandler()
