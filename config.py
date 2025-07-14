# config.py - Clean configuration without syntax errors
from pathlib import Path
import os

# --- DIRECTORY CONFIGURATION ---
try:
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    PDF_TXT_DIR = BASE_DIR / "PDF_TXT"
    CACHE_DIR = BASE_DIR / ".cache"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # Ensure critical directories exist
    for directory in [OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Warning: Cannot create directory {directory} (permission denied)")
        except Exception as e:
            print(f"Warning: Error creating directory {directory}: {e}")
    
    # Create assets directory if it doesn't exist (optional for icons)
    try:
        ASSETS_DIR.mkdir(exist_ok=True)
    except:
        pass  # Assets directory is optional

except Exception as e:
    print(f"Error setting up directories: {e}")
    # Fallback to current directory
    BASE_DIR = Path.cwd()
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    PDF_TXT_DIR = BASE_DIR / "PDF_TXT"
    CACHE_DIR = BASE_DIR / ".cache"
    ASSETS_DIR = BASE_DIR / "assets"

# --- BRANDING AND UI COLORS ---
BRAND_COLORS = {
    "kyocera_red": "#DA291C",
    "kyocera_black": "#231F20",
    "background": "#F0F2F5",
    "frame_background": "#FFFFFF",
    "header_text": "#000000",
    "accent_blue": "#0078D4",
    "success_green": "#107C10",
    "warning_orange": "#FFA500",
    "fail_red": "#DA291C",
    "highlight_blue": "#0078D4",
    
    # Status bar background colors
    "status_default_bg": "#F8F8F8",
    "status_processing_bg": "#DDEEFF",
    "status_ocr_bg": "#E6F7FF",
    "status_ai_bg": "#F9F0FF",
}

# --- DATA PROCESSING RULES ---
# Patterns to exclude from model matching
EXCLUSION_PATTERNS = [
    "CVE-",     # Security vulnerabilities
    "CWE-",     # Common weakness enumeration
    "TK-",      # Ticket references
    "HTTP",     # URLs
    "HTTPS",    # URLs
    "WWW.",     # URLs
    "ERROR",    # Error codes
    "DEBUG",    # Debug info
]

# Default model number patterns (regex)
MODEL_PATTERNS = [
    # TASKalfa series
    r'\bTASKalfa\s*[\w-]+\b',
    
    # ECOSYS series
    r'\bECOSYS\s*[\w-]+\b',
    
    # Common prefixes with numbers
    r'\b(PF|DF|MK|AK|DP|BF|JS|KM|FS)-\d+[\w-]*\b',
    
    # Specific patterns for different series
    r'\bKM-\d+\w*\b',           # KM series
    r'\bFS-\d+\w*\b',           # FS series
    r'\bM\d+\w*\b',             # M series
    r'\bP\d+\w*\b',             # P series
    
    # Color models
    r'\bKM-C\d+\w*\b',          # KM-C series
    r'\bFS-C\d+\w*\b',          # FS-C series
]

# QA and service bulletin number patterns
QA_NUMBER_PATTERNS = [
    r'\bQA[-_]?\d+\b',          # QA-1234 or QA_1234 or QA1234
    r'\bSB[-_]?\d+\b',          # SB-1234 or SB_1234 or SB1234
    r'\bQA[-_]?\w+\b',          # QA-ABC123
    r'\bSB[-_]?\w+\b',          # SB-ABC123
]

# Authors to ignore/exclude
UNWANTED_AUTHORS = [
    "Knowledge Import",
    "System",
    "Administrator",
    "Admin",
    "Auto Import",
    "Automated",
    "Bot",
    "Service",
    "",  # Empty strings
]

# Text standardization rules
STANDARDIZATION_RULES = {
    "TASKalfa-": "TASKalfa ",      # Remove dash, add space
    "ECOSYS-": "ECOSYS ",          # Remove dash, add space
    "  ": " ",                     # Replace double spaces with single
    "\t": " ",                     # Replace tabs with spaces
    "\n": " ",                     # Replace newlines with spaces
}

# --- EXCEL MAPPING ---
# Column names to look for in Excel files (case-insensitive matching)
META_COLUMN_NAME = "Meta"
AUTHOR_COLUMN_NAME = "Author"
DESCRIPTION_COLUMN_NAME = "Short description"
STATUS_COLUMN_NAME = "Processing Status"

# Excel column alternatives (in case of different naming)
COLUMN_ALTERNATIVES = {
    "Meta": ["Meta", "Metadata", "Model", "Models", "Product"],
    "Author": ["Author", "Created by", "Writer", "By"],
    "Short description": ["Short description", "Description", "Title", "Summary"],
    "Processing Status": ["Processing Status", "Status", "State", "Result"]
}

# --- PROCESSING CONFIGURATION ---
# OCR settings
OCR_DPI = 300                      # DPI for OCR rendering
OCR_MIN_TEXT_THRESHOLD = 100       # Minimum chars per page before OCR
OCR_LANGUAGES = ['eng']            # OCR languages (add 'jpn' for Japanese)

# Processing timeouts (seconds)
PDF_PROCESSING_TIMEOUT = 300       # 5 minutes per PDF
OCR_PROCESSING_TIMEOUT = 600       # 10 minutes for OCR per PDF

# Cache settings
ENABLE_CACHING = True              # Enable result caching
CACHE_MAX_AGE_DAYS = 30           # Maximum age of cached results

# --- VALIDATION FUNCTIONS ---
def validate_config():
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    # Check directories
    for name, path in [
        ("BASE_DIR", BASE_DIR),
        ("OUTPUT_DIR", OUTPUT_DIR),
        ("LOGS_DIR", LOGS_DIR),
        ("PDF_TXT_DIR", PDF_TXT_DIR),
        ("CACHE_DIR", CACHE_DIR)
    ]:
        if not path.exists():
            errors.append(f"Required directory missing: {name} = {path}")
        elif not os.access(path, os.W_OK):
            errors.append(f"No write permission for: {name} = {path}")
    
    # Check assets directory (optional)
    if not ASSETS_DIR.exists():
        warnings.append(f"Assets directory not found: {ASSETS_DIR} (icons will not be available)")
    
    # Validate patterns
    import re
    for pattern_list, list_name in [
        (MODEL_PATTERNS, "MODEL_PATTERNS"),
        (QA_NUMBER_PATTERNS, "QA_NUMBER_PATTERNS")
    ]:
        for i, pattern in enumerate(pattern_list):
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Invalid regex in {list_name}[{i}]: {pattern} - {e}")
    
    return errors, warnings

def get_column_name(target_column, available_columns):
    """
    Find the best matching column name from available columns.
    Returns the actual column name if found, None otherwise.
    """
    target_lower = target_column.lower()
    
    # First, try exact match
    for col in available_columns:
        if col and col.lower() == target_lower:
            return col
    
    # Then try alternatives
    alternatives = COLUMN_ALTERNATIVES.get(target_column, [])
    for alt in alternatives:
        alt_lower = alt.lower()
        for col in available_columns:
            if col and col.lower() == alt_lower:
                return col
    
    # Finally, try partial matching
    for col in available_columns:
        if col and target_lower in col.lower():
            return col
    
    return None

def print_config_info():
    """Print configuration information for debugging"""
    print("=" * 60)
    print("KYO QA Tool Configuration")
    print("=" * 60)
    
    print(f"Base Directory: {BASE_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print(f"PDF Text Directory: {PDF_TXT_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print(f"Assets Directory: {ASSETS_DIR}")
    
    print(f"\nModel Patterns: {len(MODEL_PATTERNS)} defined")
    print(f"QA Patterns: {len(QA_NUMBER_PATTERNS)} defined")
    print(f"Exclusion Patterns: {len(EXCLUSION_PATTERNS)} defined")
    
    # Validate configuration
    errors, warnings = validate_config()
    
    if errors:
        print(f"\n❌ Configuration Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  Configuration Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ Configuration is valid")
    
    print("=" * 60)

# Auto-validate on import
if __name__ == "__main__":
    print_config_info()
else:
    # Quick validation on import
    try:
        errors, warnings = validate_config()
        if errors:
            print(f"Config errors detected: {len(errors)} issues")
            for error in errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
    except Exception as e:
        print(f"Error validating config: {e}")
