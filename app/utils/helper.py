import os

def ensure_directories_exist(paths: list[str]):
    """Creates required upload and static folders if they don't exist."""
    for path in paths:
        os.makedirs(path, exist_ok=True)