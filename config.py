# config.py
# Version: 28.0.0
# Last modified: 2025-07-06

import json
import os
import logging
from pathlib import Path
from version import __version__
from branding import KyoceraColors

# Initialize logging
logger = logging.getLogger('config')

# --- Directory Constants ---
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
LOGS_DIR = BASE_DIR / 'logs'
ASSETS_DIR = BASE_DIR / 'assets'
PDF_TXT_DIR = OUTPUT_DIR / 'pdf_texts'
CACHE_DIR = BASE_DIR / 'cache'
NEED_REVIEW_DIR = OUTPUT_DIR
CONFIG_FILE = BASE_DIR / 'config.json'

# --- GUI and App Color Configuration ---
BRAND_COLORS = {
    "background": KyoceraColors.BACKGROUND_MAIN,
    "widget_bg": KyoceraColors.BACKGROUND_WIDGET,
    "header_bg": KyoceraColors.KYOCERA_BLACK,
    "primary_text": KyoceraColors.TEXT_PRIMARY,
    "secondary_text": KyoceraColors.TEXT_SECONDARY,
    "kyocera_red": KyoceraColors.KYOCERA_RED,
    "primary_blue": KyoceraColors.PRIMARY_BLUE,
    "status_success": KyoceraColors.STATUS_SUCCESS,
    "status_warning": KyoceraColors.STATUS_WARNING,
    "status_error": KyoceraColors.STATUS_ERROR,
    "status_info": KyoceraColors.STATUS_INFO,
}

# --- Column Names for Excel Processing ---
STATUS_COLUMN_NAME = "Validation Status"
DESCRIPTION_COLUMN_NAME = "description"
META_COLUMN_NAME = "meta"
AUTHOR_COLUMN_NAME = "author"


# --- Functions for GUI Configuration ---
DEFAULT_CONFIG = {
    'input_dir': '',
    'output_dir': str(OUTPUT_DIR.absolute()), # Store as string in JSON
}

def load_config():
    """
    Loads the configuration from config.json.
    If the file doesn't exist, it creates a default one.
    """
    if not os.path.exists(CONFIG_FILE):
        logger.info(f"Config file not found. Creating default config at {CONFIG_FILE}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {CONFIG_FILE}")
            return config
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config file: {e}. Using default config.")
        return DEFAULT_CONFIG

def save_config(config_data):
    """
    Saves the given configuration data to config.json.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
            logger.info(f"Configuration saved to {CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Error saving config file: {e}")

def get_app_version():
    """
    Returns the application version from the version.py file.
    """
    return __version__
