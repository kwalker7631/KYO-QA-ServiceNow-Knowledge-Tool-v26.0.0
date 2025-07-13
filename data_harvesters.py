# data_harvesters.py
import re
import importlib
import logging
from logging_config import configure_logging
from pathlib import Path

# Configure logging
logger = configure_logging("harvesters")

# --- Default Patterns (Single Source of Truth) ---
DEFAULT_MODEL_PATTERNS = [
    r'\b(TASKalfa|ECOSYS)\s*[\w-]+\b',
    r'\b(PF|DF|MK|AK|DP|BF|JS)-\d+[\w-]*\b',
    r'\bFS-C?\d+[a-zA-Z]*\b',
    r'\bKM-\d+[a-zA-Z]*\b',
    r'\bCS\s\d+[a-zA-Z]*\b',
]
DEFAULT_QA_PATTERNS = [r'\bQA[-_]?\d+[\w-]*\b', r'\bSB[-_]?\d+[\w-]*\b']
EXCLUSION_PATTERNS = ["CVE-", "CWE-", "TK-"]
UNWANTED_AUTHORS = ["Knowledge Import", "System Administrator"]
STANDARDIZATION_RULES = {"TASKalfa-": "TASKalfa ", "ECOSYS-": "ECOSYS "}


def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """
    Safely loads custom patterns and combines them with defaults.
    """
    all_patterns = default_patterns[:]
    try:
        custom_patterns_module = importlib.import_module("custom_patterns")
        custom_patterns_list = getattr(custom_patterns_module, pattern_name, [])
        if custom_patterns_list:
            all_patterns.extend([p for p in custom_patterns_list if p not in all_patterns])
            logger.info(f"Successfully loaded {len(custom_patterns_list)} custom patterns for '{pattern_name}'.")
    except ImportError:
        # This is not an error, just means no custom patterns are present.
        logger.info("No 'custom_patterns.py' file found. Using default patterns only.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading custom patterns: {e}")

    return all_patterns

# --- Harvester Functions ---

def harvest_models(text: str, filename: str) -> list:
    """Extracts model numbers using combined default and custom patterns."""
    if not text:
        return []

    model_patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    qa_patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)
    all_search_patterns = model_patterns + qa_patterns

    found = set()
    for pattern in all_search_patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Exclude matches containing exclusion patterns
                if not any(ex in match for ex in EXCLUSION_PATTERNS):
                    found.add(match.strip())
        except re.error as e:
            logger.warning(f"Invalid regex pattern skipped: '{pattern}'. Error: {e}")

    # Standardize results
    standardized_found = set()
    for item in found:
        for key, value in STANDARDIZATION_RULES.items():
            item = item.replace(key, value)
        standardized_found.add(item)

    return sorted(list(standardized_found))


def harvest_author(text: str) -> str:
    """Finds the author and returns an empty string if it's an unwanted name."""
    if not text:
        return ""

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
                if author and author not in UNWANTED_AUTHORS:
                    return author
        except Exception as e:
            logger.error(f"Error extracting author with pattern {pattern}: {e}")

    return ""


def harvest_qa_numbers(text: str) -> list:
    """Extracts QA numbers using only QA_NUMBER_PATTERNS."""
    if not text:
        return []

    qa_patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)

    found = set()
    for pattern in qa_patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if not any(ex in match for ex in EXCLUSION_PATTERNS):
                    found.add(match.strip())
        except re.error as e:
            logger.warning(
                f"Invalid regex pattern skipped: '{pattern}'. Error: {e}"
            )

    standardized_found = set()
    for item in found:
        for key, value in STANDARDIZATION_RULES.items():
            item = item.replace(key, value)
        standardized_found.add(item)

    return sorted(list(standardized_found))

def harvest_all_data(text: str, filename: str) -> dict:
    """The main harvester function that aggregates all data."""
    if not text and not filename:
        logger.warning("No text or filename provided for data harvesting")
        return {"models": "Not Found", "author": ""}

    try:
        models = harvest_models(text, filename)
        models_str = ", ".join(models) if models else "Not Found"
        qa_numbers = harvest_qa_numbers(text)
        qa_numbers_str = ", ".join(qa_numbers) if qa_numbers else ""
        author_str = harvest_author(text)

        return {
            "models": models_str,
            "qa_numbers": qa_numbers_str,
            "author": author_str,
        }
    except Exception as e:
        logger.error(f"Critical error during data harvesting for {filename}: {e}", exc_info=True)
        return {"models": "Error: Harvesting Failed", "author": ""}
