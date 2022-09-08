import json
from pathlib import Path
from typing import TypedDict


class ProxyServerSettings(TypedDict):
    HOST: str
    PORT: int
    REQUESTED_URL: str


class TextModifyingSettings(TypedDict):
    WORDS_LENGTH: int
    ADD_CHARACTER: str


class Settings:
    """Represents settings of the project."""

    @classmethod
    def read_config_file(cls, file_path: str | Path) -> 'Settings':
        """
        Reads the config json-file and returns the instance of
        `Settings` with data of this file.
        """
        with open(file_path) as file:
            config_data = json.load(file)
        return cls(config_data)

    def __init__(self, config_dict: dict):
        self.config = config_dict
        self.proxy_settings: ProxyServerSettings = self.config.get('PROXY_SERVER', {})
        self.text_modifying: TextModifyingSettings = self.config.get('TEXT_MODIFYING', {})


settings = Settings.read_config_file(Path(__file__).parent / 'config.json')
