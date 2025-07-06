# branding.py
# Version: 31.0.0
# Last modified: 2025-07-06

class KyoceraColors:
    """
    Defines a high-contrast color palette for the application.
    """
    # --- Primary Branding ---
    KYOCERA_RED = "#DA291C"
    
    # --- UI Palette for High Visibility ---
    BACKGROUND_MAIN = "#F0F2F5"       # Light grey for the main window
    WIDGET_BG = "#FFFFFF"             # White for input fields and cards
    
    TEXT_DARK = "#212529"             # Very dark grey for primary text
    TEXT_MUTED = "#6c757d"            # Muted grey for secondary labels
    
    PRIMARY_ACTION = "#0d6efd"        # A strong blue for primary buttons
    PRIMARY_ACTION_HOVER = "#0b5ed7"  # A darker blue for hover
    
    BORDER_COLOR = "#ced4da"          # A clear border color for widgets
    
    # --- Status Colors ---
    STATUS_SUCCESS = "#198754"        # Green for success
    STATUS_WARNING = "#ffc107"        # Yellow for warnings
    STATUS_ERROR = "#dc3545"          # Red for errors
    STATUS_INFO_TEXT = "#0dcaf0"      # Cyan for informational link buttons

    # Backwards compatibility aliases
    BACKGROUND_WIDGET = WIDGET_BG
    KYOCERA_BLACK = "#000000"
    TEXT_PRIMARY = TEXT_DARK
    TEXT_SECONDARY = TEXT_MUTED
    PRIMARY_BLUE = PRIMARY_ACTION
    STATUS_INFO = STATUS_INFO_TEXT
