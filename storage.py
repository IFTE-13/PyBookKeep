"""Storage module for PyLibrary.

Handles reading, writing, and initializing JSON data files safely.
Provides graceful error handling for missing, corrupted, or unreadable files.
"""

import json
import os
import shutil
from typing import Any, Dict, List, Optional

# Default directory for persistent JSON data
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get_data_path(filename: str, data_dir: Optional[str] = None) -> str:
    """Return the absolute path for a data file."""
    base_dir = data_dir if data_dir is not None else DEFAULT_DATA_DIR
    return os.path.join(base_dir, filename)


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure that the target directory exists, creating it if needed."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def load_json(file_path: str, default_data: Any = None) -> Any:
    """Load and parse a JSON file safely.

    If the file does not exist, return default_data (or empty list/dict).
    If the file is empty or corrupted, raise a ValueError or return default_data
    while preserving the damaged file for recovery.
    """
    if not os.path.exists(file_path):
        return default_data if default_data is not None else []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                # File is empty
                return default_data if default_data is not None else []
            return json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        # File is malformed; do not overwrite it silently
        raise ValueError(
            f"Failed to decode JSON from '{file_path}': {error}. "
            "Data was not modified to prevent data loss."
        ) from error
    except OSError as error:
        raise OSError(f"Could not read file '{file_path}': {error}") from error


def save_json(file_path: str, data: Any) -> None:
    """Write data to a JSON file atomically using a temporary file.

    This prevents data corruption if an error or crash occurs during writing.
    """
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)

    temp_file_path = f"{file_path}.tmp"
    try:
        with open(temp_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())

        # Atomic replacement on Windows and POSIX
        if os.path.exists(file_path):
            os.replace(temp_file_path, file_path)
        else:
            shutil.move(temp_file_path, file_path)
    except Exception as error:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass
        raise OSError(f"Failed to write data to '{file_path}': {error}") from error


def initialize_file_if_missing(file_path: str, default_content: Any) -> bool:
    """Create and initialize a file with default content only if it doesn't exist."""
    if not os.path.exists(file_path):
        save_json(file_path, default_content)
        return True
    return False
