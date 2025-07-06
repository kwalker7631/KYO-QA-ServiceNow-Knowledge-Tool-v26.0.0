# version.py
# Version: 26.0.0
# Last modified: 2025-07-06

# The version number used throughout the application
__version__ = "26.0.0"

# Alias for backward compatibility
VERSION = __version__

def get_version():
    """Return the current application version."""
    return __version__