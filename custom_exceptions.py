# custom_exceptions.py
# Version: 1.0.1
# Last modified: 2025-07-13

"""
Custom exception classes for the application.
"""

class ProcessingError(Exception):
    """Custom exception for errors during the file processing workflow."""
    pass

class APIError(Exception):
    """Custom exception for errors related to external API calls."""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

# === AUTO-GENERATED FUNCTIONS FOR CUSTOM_EXCEPTIONS ===
# Add these functions to custom_exceptions.py


class FileLockError(Exception):
    """Exception for file lock errors."""
    pass
