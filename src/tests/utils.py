from pathlib import Path


def get_path_to_source_file(*filenames: str) -> str:
    """Returns path to the file in the `source` directory."""
    parent_path = Path(__file__).parent
    for filename in filenames:
        parent_path /= filename
    return str(parent_path.resolve())
