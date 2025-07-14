# file_utils.py
# Version: 1.2.0
# Last modified: 2025-07-13

import os
import shutil
import logging
import tempfile
import zipfile
import json
from pathlib import Path
from typing import Dict, Any, Optional

from config import TEMP_DIR, CACHE_DIR, OUTPUT_DIR

logger = logging.getLogger(__name__)


def ensure_folders():
    """Ensure that necessary application folders exist."""
    for folder in [TEMP_DIR, CACHE_DIR, OUTPUT_DIR]:
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory {folder}: {e}")
            # Depending on the folder, you might want to raise the exception
            # or handle it more gracefully.
            raise


def cleanup_directory(directory_path: str, clear_all: bool = False):
    """
    Cleans up a directory by removing its contents.
    If clear_all is True, removes the directory itself.
    """
    path = Path(directory_path)
    if not path.exists():
        logger.warning(f"Directory not found for cleanup: {directory_path}")
        return

    try:
        if clear_all:
            shutil.rmtree(path)
            logger.info(f"Removed directory: {path}")
        else:
            for item in path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            logger.info(f"Cleaned contents of directory: {path}")
    except (OSError, shutil.Error) as e:
        logger.error(f"Error cleaning up directory {path}: {e}")


def extract_zip_to_temp(zip_path: Path) -> Optional[Path]:
    """
    Extracts a zip file to a new temporary directory.
    Returns the path to the temporary directory, or None on failure.
    """
    try:
        temp_dir = Path(tempfile.mkdtemp(dir=TEMP_DIR))
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        logger.info(f"Extracted '{zip_path.name}' to '{temp_dir}'")
        return temp_dir
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        logger.error(f"Failed to extract zip file {zip_path}: {e}")
        return None


def open_file_in_default_app(file_path: str):
    """
    Opens a file with the default application for the current OS.
    """
    try:
        os.startfile(file_path)
    except AttributeError:  # Fallback for non-Windows systems
        import subprocess
        try:
            subprocess.run(['open', file_path], check=True)  # macOS
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                subprocess.run(['xdg-open', file_path], check=True)  # Linux
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                logger.error(f"Could not open file {file_path}. Error: {e}")


def save_to_cache(filename: str, data: Dict[str, Any]) -> None:
    """
    Saves processed data to a JSON file in the cache directory.
    The cache filename is derived from the original filename.
    """
    try:
        # Sanitize filename to create a valid cache filename
        cache_filename = Path(filename).stem + ".json"
        cache_path = CACHE_DIR / cache_filename
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved results for '{filename}' to cache: {cache_path}")

    except (IOError, TypeError) as e:
        logger.error(f"Failed to save data to cache for {filename}: {e}")

