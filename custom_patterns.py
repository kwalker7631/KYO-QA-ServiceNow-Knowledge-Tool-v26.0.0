# custom_patterns.py
# Version: 2.2.1
# Last modified: 2025-07-13

import logging
import json
from pathlib import Path

# This file should not import from other project modules to avoid circular dependencies.

logger = logging.getLogger(__name__)

# --- Path Setup ---
# Use an absolute path based on this file's location to ensure robustness.
try:
    APP_ROOT = Path(__file__).resolve().parent
except NameError:
    # Fallback for environments where __file__ is not defined (e.g., some frozen executables)
    APP_ROOT = Path.cwd()
PATTERNS_DIR = APP_ROOT / "patterns"

# --- Default Content ---
# These patterns will be written to JSON files if they don't exist.
DEFAULT_PATTERNS = {
    "model_patterns.json": [
        "TASKalfa\\s*\\d{4}ci",
        "ECOSYS\\s*M\\d{4}cidn",
        "CS\\s*\\d{4}ci"
    ],
    "qa_number_patterns.json": [
        # This pattern is more robust. It looks for "QA" followed by
        # an underscore or a space, and then one or more digits.
        # It will match formats like "QA_20141" or "QA 12345".
        "QA[ _]\\d+"
    ]
}

def _initialize_patterns():
    """
    Ensures the patterns directory and default JSON files exist.
    This function is designed to be run once at startup.
    """
    try:
        if not PATTERNS_DIR.exists():
            logger.warning(f"Patterns directory not found at '{PATTERNS_DIR}'. Creating it.")
            PATTERNS_DIR.mkdir(parents=True, exist_ok=True)

        for filename, patterns in DEFAULT_PATTERNS.items():
            file_path = PATTERNS_DIR / filename
            if not file_path.exists():
                logger.warning(f"Pattern file '{file_path}' not found. Creating it with default patterns.")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(patterns, f, indent=4)

    except Exception as e:
        logger.critical(f"Failed to initialize the patterns directory or files. Error: {e}", exc_info=True)
        raise RuntimeError("Could not create necessary pattern files.") from e

def _load_patterns_from_json(file_path: Path) -> list:
    """Loads patterns from a specific JSON file."""
    if not file_path.exists():
        logger.error(f"Cannot load patterns: File does not exist at '{file_path}'.")
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load or parse patterns from {file_path}: {e}")
        return []

# --- Main Loading Logic ---
_initialize_patterns() 

MODEL_PATTERNS = _load_patterns_from_json(PATTERNS_DIR / "model_patterns.json")
QA_NUMBER_PATTERNS = _load_patterns_from_json(PATTERNS_DIR / "qa_number_patterns.json")

_pattern_registry = {
    "MODEL_PATTERNS": MODEL_PATTERNS,
    "QA_NUMBER_PATTERNS": QA_NUMBER_PATTERNS,
}

def get_patterns(name: str) -> list:
    """Retrieves a list of patterns by its registered name."""
    patterns = _pattern_registry.get(name, [])
    logger.info(f"Retrieved {len(patterns)} patterns for '{name}'.")
    return patterns
