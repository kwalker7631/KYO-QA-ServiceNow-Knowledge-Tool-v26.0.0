# file_utils.py
# Version: 32.6.0
# Last modified: 2025-07-06

import os
import sys
import shutil
import tempfile
import logging
from logging_config import configure_logging
import platform
import subprocess # FIXED: Added missing import
from tkinter import messagebox
from pathlib import Path
import stat
import zipfile

# Configure logging
logger = configure_logging(__name__)

def try_unlock_file(filepath: Path) -> bool:
    """Attempts to remove the read-only attribute from a file."""
    try:
        current_permissions = os.stat(filepath).st_mode
        os.chmod(filepath, current_permissions | stat.S_IWRITE)
        return True
    except (OSError, PermissionError) as e:
        logger.warning(f"Could not change file attributes for {filepath.name}: {e}")
        return False

def get_resource_path(relative_path):
    """Get the absolute path to a resource, for dev and PyInstaller."""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path.cwd()
    return base_path / relative_path

def is_file_locked(filepath: Path) -> bool:
    """Checks if a file is locked by attempting to open it in exclusive mode."""
    try:
        with open(filepath, 'r+b'):
            pass
        return False
    except (IOError, PermissionError):
        return True

def extract_zip_to_temp(zip_path: Path) -> Path | None:
    """Extracts a ZIP archive to a temporary directory."""
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix="kyo_qa_"))
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)
        logger.info(f"Successfully extracted {zip_path.name} to {temp_dir}")
        return temp_dir
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        logger.error(f"Failed to extract zip file {zip_path.name}: {e}")
        return None

def cleanup_directory(dir_path: Path):
    """Recursively removes a directory and its contents."""
    try:
        if dir_path and dir_path.exists():
            shutil.rmtree(dir_path)
    except Exception as e:
        logger.error(f"Failed to clean up temporary directory {dir_path}: {e}")

def open_file_in_default_app(filepath: str | Path):
    """Opens a file with the default system application (cross-platform)."""
    filepath = Path(filepath)
    if not filepath.exists():
        msg = f"Could not open file because it does not exist:\n{filepath}"
        logger.error(msg)
        messagebox.showerror("File Not Found", msg)
        return
        
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', filepath], check=True)
        else:  # Linux and other Unix-like OS
            subprocess.run(['xdg-open', filepath], check=True)
    except Exception as e:
        msg = f"Could not open the file with the default application:\n{filepath}\n\nError: {e}"
        logger.error(msg, exc_info=True)
        messagebox.showerror("Error", msg)

def ensure_folders():
    """Creates all necessary application directories on startup."""
    from config import OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR, NEED_REVIEW_DIR
    
    for directory in [OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    (NEED_REVIEW_DIR / "needs_review").mkdir(parents=True, exist_ok=True)
