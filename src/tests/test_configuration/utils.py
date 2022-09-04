from pathlib import Path


def get_path_to_source_file(filename: str) -> str:
    """Returns path to the file in the `source` directory."""
    return str((Path(__file__).parent / 'source' / filename).resolve())
