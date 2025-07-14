# data_harvesters.py
# Version: 2.5.0
# Last modified: 2025-07-13

import re
import logging
from typing import List, Dict, Any, Optional

from custom_patterns import get_patterns

logger = logging.getLogger(__name__)

def _harvest_from_patterns(text: str, pattern_name: str) -> List[str]:
    """Generic helper to find all matches for a given pattern name."""
    patterns = get_patterns(pattern_name)
    if not patterns:
        logger.warning(f"No patterns found for '{pattern_name}'.")
        return []
    
    all_matches = set()
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches and isinstance(matches[0], tuple):
                for match_tuple in matches:
                    for group in match_tuple:
                        if group:
                            all_matches.add(group.strip())
            else:
                for match in matches:
                    all_matches.add(match.strip())
        except re.error as e:
            logger.error(f"Regex error for pattern '{pattern}' in '{pattern_name}': {e}")
            
    return sorted(list(all_matches))

def harvest_models(text: str) -> List[str]:
    """Harvests device model numbers from the text."""
    return _harvest_from_patterns(text, "MODEL_PATTERNS")

def harvest_qa_number(text: str) -> Optional[str]:
    """Harvests the primary QA number from the text."""
    matches = _harvest_from_patterns(text, "QA_NUMBER_PATTERNS")
    return matches[0] if matches else None

def harvest_author(text: str) -> Optional[str]:
    """Harvests the author's name from the text."""
    match = re.search(r"Author:\s*(.*)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown"

def harvest_all_data(text: str, filename: str) -> Dict[str, Any]:
    """
    Runs all data harvesters and returns a structured dictionary.
    Device models are placed in a nested 'meta' dictionary.
    """
    models = harvest_models(text)
    qa_number = harvest_qa_number(text)
    author = harvest_author(text)

    # This structure places the models inside a 'meta' field as requested.
    data = {
        "filename": filename,
        "qa_number": qa_number,
        "author": author,
        "meta": {
            "models": models,
        },
    }
    logger.info(f"Harvested data for {filename}: QA={qa_number}, Models={len(models)}")
    return data
