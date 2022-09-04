from pathlib import Path

import pytest

from configuration.settings import settings, read_config_file
from tests.test_configuration.utils import get_path_to_source_file


def test_settings_instance_is_dict():
    assert isinstance(settings, dict)


def test_settings_has_all_required_values():
    assert "PROXY_SERVER" in settings
    assert "HOST" in settings["PROXY_SERVER"]
    assert "PORT" in settings["PROXY_SERVER"]
    assert "REQUESTED_URL" in settings["PROXY_SERVER"]


@pytest.mark.parametrize(
    'config_filename',
    [
        'test_config1.json',
        'test_config2.json',
    ]
)
def test_read_config_file_function_accepts_strings(config_filename):
    assert isinstance(read_config_file(get_path_to_source_file(config_filename)), dict)


@pytest.mark.parametrize(
    'config_filename',
    [
        'test_config1.json',
        'test_config2.json',
    ]
)
def test_read_config_file_function_accepts_path_parameter(config_filename):
    assert isinstance(read_config_file(Path(__file__).parent / 'source' / config_filename), dict)


def test_read_config_file_function_returns_all_values():
    config_data = read_config_file(get_path_to_source_file('test_config1.json'))
    assert "PROXY_SERVER" in config_data
    assert "HOST" in config_data["PROXY_SERVER"]
    assert "PORT" in config_data["PROXY_SERVER"]
    assert "REQUESTED_URL" in config_data["PROXY_SERVER"]

    config_data = read_config_file(get_path_to_source_file('test_config2.json'))
    assert not config_data
