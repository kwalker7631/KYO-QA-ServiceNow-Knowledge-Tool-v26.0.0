# config.py
# Version: 2.1.0
# Last modified: 2025-07-13

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Core Application Paths ---
# Use Path(__file__).resolve().parent to get the directory of the current script.
# This makes the paths relative to the application's location, ensuring it works anywhere.
APP_ROOT = Path(__file__).resolve().parent

# Define the directories for temporary files, cache, and output
TEMP_DIR = APP_ROOT / "temp"
CACHE_DIR = APP_ROOT / "cache"
OUTPUT_DIR = APP_ROOT / "output"

# --- Tesseract OCR Configuration ---
# Path to the Tesseract executable.
# This needs to be configured by the user if it's not in the system's PATH.
TESSERACT_CMD = "tesseract"

# --- Function to load settings from config.json ---
def load_settings():
    """
    Loads settings from the config.json file.
    Returns a dictionary with the settings, or a default dictionary on error.
    """
    try:
        config_path = APP_ROOT / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                logger.info("Configuration loaded from config.json")
                return settings
        else:
            logger.warning("config.json not found. Using default settings.")
            return {}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config.json: {e}")
        return {}

# --- Load settings on startup ---
SETTINGS = load_settings()

# --- API Configuration (Example) ---
# You can retrieve API keys or other settings like this:
API_KEY = SETTINGS.get("api_key", "default_api_key_if_not_found")

