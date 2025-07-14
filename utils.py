# utils.py
# Version: 2.0.0
# Last modified: 2025-07-13

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def load_patterns_from_json(file_path: str) -> List[str]:
    """
    Loads a list of regex patterns from a JSON file.
    
    Args:
        file_path: The path to the JSON file.

    Returns:
        A list of patterns, or an empty list if an error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load patterns from {file_path}: {e}")
        return []

# The ExcelGenerator class has been moved to its own file (excel_generator.py)
# to maintain a clear and non-circular project structure. 
# The debugging code that was previously here and causing the circular import
# has been removed.

