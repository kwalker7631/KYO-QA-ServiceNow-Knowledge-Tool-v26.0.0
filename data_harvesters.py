# data_harvesters.py - Fixed version with corrected function calls
import re
import importlib
from pathlib import Path
from config import (
    MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS,
    QA_NUMBER_PATTERNS as DEFAULT_QA_PATTERNS,
    EXCLUSION_PATTERNS,
    UNWANTED_AUTHORS,
    STANDARDIZATION_RULES,
)

def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """Safely loads and combines default and custom patterns."""
    custom_patterns = []
    try:
        custom_mod = importlib.import_module("custom_patterns")
        importlib.reload(custom_mod)
        custom_patterns = getattr(custom_mod, pattern_name, [])
        print(f"Loaded {len(custom_patterns)} custom {pattern_name}")
    except (ImportError, SyntaxError, AttributeError) as e:
        print(f"Could not load custom patterns for {pattern_name}: {e}")
    
    # Combine custom and default patterns, avoiding duplicates
    combined = custom_patterns + [p for p in default_patterns if p not in custom_patterns]
    print(f"Total {pattern_name}: {len(combined)} patterns")
    return combined

def is_excluded(text: str) -> bool:
    """Checks if a string contains any of the unwanted exclusion patterns."""
    if not text:
        return True
    
    text_lower = text.lower()
    for pattern in EXCLUSION_PATTERNS:
        if pattern.lower() in text_lower:
            return True
    return False

def clean_model_string(model_str: str) -> str:
    """Applies standardization rules to a found model string."""
    if not model_str:
        return ""
    
    cleaned = model_str.strip()
    
    # Apply standardization rules
    for rule, replacement in STANDARDIZATION_RULES.items():
        cleaned = cleaned.replace(rule, replacement)
    
    return cleaned

def harvest_models(text: str, filename: str) -> list:
    """
    Finds all unique models from text and filename, respecting exclusions.
    Returns a list of cleaned model strings.
    """
    if not text and not filename:
        return []
    
    models = set()
    patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    
    # Search in both text content and filename
    search_content = [
        text or "",
        filename.replace("_", " ").replace("-", " ") if filename else ""
    ]
    
    for content in search_content:
        if not content:
            continue
            
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle tuple matches from groups
                    if isinstance(match, tuple):
                        match = ' '.join(filter(None, match))
                    
                    if match and not is_excluded(match):
                        cleaned = clean_model_string(match)
                        if cleaned:  # Only add non-empty cleaned strings
                            models.add(cleaned)
                            
            except re.error as e:
                print(f"Invalid regex pattern '{pattern}': {e}")
                continue
    
    return sorted(list(models))

def harvest_qa_numbers(text: str, filename: str) -> list:
    """
    Finds all unique QA/SB numbers from text and filename.
    Returns a list of QA number strings.
    """
    if not text and not filename:
        return []
    
    qa_numbers = set()
    patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)
    
    # Search in both text content and filename
    search_content = [
        text or "",
        filename.replace("_", " ").replace("-", " ") if filename else ""
    ]
    
    for content in search_content:
        if not content:
            continue
            
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle tuple matches from groups
                    if isinstance(match, tuple):
                        match = ' '.join(filter(None, match))
                    
                    if match and not is_excluded(match):
                        cleaned = match.strip()
                        if cleaned:
                            qa_numbers.add(cleaned)
                            
            except re.error as e:
                print(f"Invalid regex pattern '{pattern}': {e}")
                continue
    
    return sorted(list(qa_numbers))

def harvest_author(text: str) -> str:
    """
    Finds the author and returns an empty string if it's an unwanted name.
    Searches for various author patterns in the text.
    """
    if not text:
        return ""
    
    # Multiple patterns to find author information
    author_patterns = [
        r"^Author:\s*(.*?)$",  # "Author: Name"
        r"^Created by:\s*(.*?)$",  # "Created by: Name"
        r"^By:\s*(.*?)$",  # "By: Name"
        r"^Writer:\s*(.*?)$",  # "Writer: Name"
        r"^\s*Author\s*[-:]\s*(.*?)$",  # "Author - Name" or "Author: Name"
    ]
    
    for pattern in author_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            author = match.strip()
            
            # Skip if empty or in unwanted list
            if not author or author in UNWANTED_AUTHORS:
                continue
            
            # Skip if it looks like a system name or ID
            if any(unwanted.lower() in author.lower() for unwanted in ["import", "system", "auto", "bot"]):
                continue
            
            # Return the first valid author found
            return author
    
    return ""

def harvest_description(text: str, filename: str) -> str:
    """
    Extract a brief description from the document.
    Uses the first meaningful paragraph or sentence.
    """
    if not text:
        return ""
    
    # Split into lines and find the first substantial content
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines, headers, and very short lines
        if len(line) < 20:
            continue
        
        # Skip lines that look like metadata
        if any(skip in line.lower() for skip in ['author:', 'date:', 'version:', 'page', 'file:']):
            continue
        
        # If we find a substantial line, use it as description
        if len(line) > 30 and len(line) < 200:
            return line
    
    # Fallback: use filename-based description
    if filename:
        name_parts = Path(filename).stem.replace('_', ' ').replace('-', ' ')
        return f"Document: {name_parts}"
    
    return "No description available"

def harvest_all_data(text: str, filename: str) -> dict:
    """
    The main harvester function that aggregates all data extraction.
    Returns a dictionary with all extracted information.
    """
    try:
        # Extract models
        models_list = harvest_models(text, filename)
        models_str = ", ".join(models_list) if models_list else "Not Found"
        
        # Extract QA numbers
        qa_numbers = harvest_qa_numbers(text, filename)
        qa_str = ", ".join(qa_numbers) if qa_numbers else ""
        
        # Extract author
        author_str = harvest_author(text)
        
        # Extract description
        description_str = harvest_description(text, filename)
        
        # Create result dictionary
        result = {
            "models": models_str,
            "qa_numbers": qa_str,
            "author": author_str,
            "description": description_str,
            "extraction_stats": {
                "models_found": len(models_list),
                "qa_numbers_found": len(qa_numbers),
                "has_author": bool(author_str),
                "text_length": len(text) if text else 0
            }
        }
        
        return result
        
    except Exception as e:
        print(f"Error in harvest_all_data: {e}")
        return {
            "models": "Error: Extraction Failed",
            "qa_numbers": "",
            "author": "",
            "description": f"Error processing {filename}",
            "extraction_stats": {
                "models_found": 0,
                "qa_numbers_found": 0,
                "has_author": False,
                "text_length": 0
            }
        }

def test_patterns_on_text(text: str, filename: str = "test.pdf"):
    """
    Test pattern matching on provided text for debugging purposes.
    Returns detailed extraction results.
    """
    print("=" * 60)
    print(f"Testing patterns on: {filename}")
    print("=" * 60)
    
    result = harvest_all_data(text, filename)
    
    print(f"Models found: {result['models']}")
    print(f"QA numbers found: {result['qa_numbers']}")
    print(f"Author found: {result['author']}")
    print(f"Description: {result['description'][:100]}...")
    print(f"Stats: {result['extraction_stats']}")
    
    return result

# Test functionality if run directly
if __name__ == "__main__":
    print("Data Harvesters - Pattern Testing")
    print("=" * 40)
    
    # Test with sample text
    sample_text = """
    Author: John Smith
    
    This document describes the TASKalfa 3252ci printer model.
    QA-12345 addresses issues with the FS-1030D scanner.
    
    For ECOSYS M3040dn troubleshooting, see the manual.
    """
    
    sample_filename = "QA_12345_TASKalfa_3252ci_manual.pdf"
    
    print("Testing with sample text...")
    test_patterns_on_text(sample_text, sample_filename)
