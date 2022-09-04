import json
from pathlib import Path
from typing import TypedDict


class ProxyServerSettings(TypedDict):
    HOST: str
    PORT: int
    REQUESTED_URL: str


class Settings(TypedDict):
    PROXY_SERVER: ProxyServerSettings


def read_config_file(file_path: str | Path) -> dict:
    """
    Reads the config json-file and returns its data as a
    dict instance.
    """
    with open(file_path) as file:
        config_data = json.load(file)
    return config_data


settings: Settings = read_config_file(Path(__file__).parent / 'config.json')
