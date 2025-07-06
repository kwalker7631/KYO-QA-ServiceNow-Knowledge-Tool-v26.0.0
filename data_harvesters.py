# data_harvesters.py
import re
import importlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("harvesters")

# Import from config with fallback values
try:
    from config import (
        MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS,
        QA_NUMBER_PATTERNS as DEFAULT_QA_PATTERNS,
        EXCLUSION_PATTERNS,
        UNWANTED_AUTHORS,
        STANDARDIZATION_RULES,
    )
except ImportError:
    # Fallback values if config import fails
    DEFAULT_MODEL_PATTERNS = [
        r'\bTASKalfa\s*[\w-]+\b',
        r'\bECOSYS\s*[\w-]+\b',
        r'\b(PF|DF|MK|AK|DP|BF|JS)-\d+[\w-]*\b',
    ]
    DEFAULT_QA_PATTERNS = [r'\bQA[-_]?[\w-]+', r'\bSB[-_]?[\w-]+']
    EXCLUSION_PATTERNS = ["CVE-", "CWE-", "TK-"]
    UNWANTED_AUTHORS = ["Knowledge Import"]
    STANDARDIZATION_RULES = {"TASKalfa-": "TASKalfa ", "ECOSYS-": "ECOSYS "}

def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """Safely loads and combines default and custom patterns."""
    custom_patterns = []
    try:
        # First check if custom_patterns.py exists
        if not Path("custom_patterns.py").exists():
            logger.warning("custom_patterns.py not found. Using default patterns only.")
            return default_patterns
            
        # Try to import custom patterns
        custom_mod = importlib.import_module("custom_patterns")
        importlib.reload(custom_mod)
        custom_patterns = getattr(custom_mod, pattern_name, [])
        logger.info(f"Loaded {len(custom_patterns)} custom patterns for {pattern_name}")
    except (ImportError, SyntaxError) as e:
        logger.warning(f"Error loading custom patterns: {e}. Using default patterns only.")
        return default_patterns
    
    # Combine custom and default patterns, removing duplicates
    combined = custom_patterns + [p for p in default_patterns if p not in custom_patterns]
    logger.info(f"Using {len(combined)} total patterns for {pattern_name}")
    return combined

def is_excluded(text: str) -> bool:
    """Checks if a string contains any of the unwanted exclusion patterns."""
    if not text:
        return True
    for pattern in EXCLUSION_PATTERNS:
        if pattern.lower() in text.lower():
            return True
    return False

def clean_model_string(model_str: str) -> str:
    """Applies standardization rules to a found model string."""
    if not model_str:
        return ""
    cleaned = model_str
    for rule, replacement in STANDARDIZATION_RULES.items():
        cleaned = cleaned.replace(rule, replacement)
    return cleaned.strip()

def harvest_models(text: str, filename: str) -> list:
    """Finds all unique models from text and filename, respecting exclusions."""
    if not text and not filename:
        logger.warning("No text or filename provided for model harvesting")
        return []
        
    models = set()
    patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    
    for content in [text, filename.replace("_", " ")]:
        if not content:
            continue
            
        for pattern in patterns:
            try:
                for match in re.findall(pattern, content, re.IGNORECASE):
                    if not is_excluded(match):
                        models.add(clean_model_string(match))
            except re.error as e:
                logger.error(f"Invalid regex pattern: {pattern}, Error: {e}")
            except Exception as e:
                logger.error(f"Error processing pattern {pattern}: {e}")
                
    return sorted(list(models))

def harvest_author(text: str) -> str:
    """Finds the author and returns an empty string if it's an unwanted name."""
    if not text:
        return ""
        
    # Common author patterns
    author_patterns = [
        r"Author:\s*(.*?)(?:\n|$)",
        r"Created by:\s*(.*?)(?:\n|$)",
        r"Written by:\s*(.*?)(?:\n|$)"
    ]
    
    for pattern in author_patterns:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                author = match.group(1).strip()
                # Ensure the found author is not in the unwanted list
                if author and author not in UNWANTED_AUTHORS:
                    return author
        except Exception as e:
            logger.error(f"Error extracting author with pattern {pattern}: {e}")
            
    return ""

def harvest_all_data(text: str, filename: str) -> dict:
    """The main harvester function that aggregates all data."""
    if not text and not filename:
        logger.warning("No text or filename provided for data harvesting")
        return {"models": "Not Found", "author": ""}
    
    try:
        models = harvest_models(text, filename)
        models_str = ", ".join(models) if models else "Not Found"
        author_str = harvest_author(text)
        
        return {"models": models_str, "author": author_str}
    except Exception as e:
        logger.error(f"Error in harvest_all_data: {e}")
        return {"models": "Not Found", "author": ""}