from pathlib import Path

import pytest

from configuration.settings import settings, Settings
from tests.utils import get_path_to_source_file


source_directory = ['test_configuration', 'source']


def test_settings_instance_is_settings_type():
    assert isinstance(settings, Settings)


def test_settings_has_all_required_values():
    assert settings.proxy_settings
    assert "HOST" in settings.proxy_settings
    assert "PORT" in settings.proxy_settings
    assert "REQUESTED_URL" in settings.proxy_settings
    assert settings.text_modifying
    assert "WORDS_LENGTH" in settings.text_modifying
    assert "ADD_CHARACTER" in settings.text_modifying


@pytest.mark.parametrize(
    'config_filename',
    [
        'test_config1.json',
        'test_config2.json',
    ]
)
def test_read_config_file_function_accepts_strings(config_filename):
    assert Settings.read_config_file(get_path_to_source_file(*source_directory, config_filename))


@pytest.mark.parametrize(
    'config_filename',
    [
        'test_config1.json',
        'test_config2.json',
    ]
)
def test_read_config_file_function_accepts_path_parameter(config_filename):
    assert Settings.read_config_file(Path(__file__).parent / 'source' / config_filename)


def test_read_config_file_function_returns_all_values():
    config_data = Settings.read_config_file(get_path_to_source_file(*source_directory, 'test_config1.json'))
    assert "HOST" in config_data.proxy_settings
    assert "PORT" in config_data.proxy_settings
    assert "REQUESTED_URL" in config_data.proxy_settings

    config_data = Settings.read_config_file(get_path_to_source_file(*source_directory, 'test_config2.json'))
    assert not config_data.proxy_settings
    assert not config_data.text_modifying
