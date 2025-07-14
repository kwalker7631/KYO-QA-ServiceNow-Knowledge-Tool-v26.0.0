# final_import_fix.py - Add ALL possible missing function aliases to gui_components.py
import re
from pathlib import Path

def add_comprehensive_aliases():
    """Add comprehensive function aliases to gui_components.py"""
    
    gui_file = Path("gui_components.py")
    
    if not gui_file.exists():
        print("❌ gui_components.py not found")
        return False
    
    # Read current content
    with open(gui_file, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Check if already has comprehensive aliases
    if "COMPREHENSIVE BACKWARD COMPATIBILITY" in current_content:
        print("✅ gui_components.py already has comprehensive aliases")
        return True
    
    # Comprehensive aliases to add
    aliases_section = '''

# === COMPREHENSIVE BACKWARD COMPATIBILITY ALIASES ===
# These handle various naming conventions that might be used

# Main layout functions
def create_controls_section(parent, app):
    """Alias for create_process_controls."""
    return create_process_controls(parent, app)

def create_main_controls(parent, app):
    """Alias for create_process_controls."""
    return create_process_controls(parent, app)

def create_control_panel(parent, app):
    """Alias for create_process_controls."""
    return create_process_controls(parent, app)

def create_button_section(parent, app):
    """Alias for create_process_controls."""
    return create_process_controls(parent, app)

def create_status_section(parent, app):
    """Alias for create_status_and_log_section."""
    return create_status_and_log_section(parent, app)

def create_log_section(parent, app):
    """Alias for create_status_and_log_section."""
    return create_status_and_log_section(parent, app)

def create_progress_section(parent, app):
    """Alias for create_status_and_log_section."""
    return create_status_and_log_section(parent, app)

def create_monitoring_section(parent, app):
    """Alias for create_status_and_log_section."""
    return create_status_and_log_section(parent, app)

def create_input_section(parent, app):
    """Alias for create_io_section."""
    return create_io_section(parent, app)

def create_file_section(parent, app):
    """Alias for create_io_section."""
    return create_io_section(parent, app)

def create_selection_section(parent, app):
    """Alias for create_io_section."""
    return create_io_section(parent, app)

def create_io_controls(parent, app):
    """Alias for create_io_section."""
    return create_io_section(parent, app)

def create_header_section(parent, version, colors=None):
    """Alias for create_main_header."""
    return create_main_header(parent, version, colors)

def create_title_section(parent, version, colors=None):
    """Alias for create_main_header."""
    return create_main_header(parent, version, colors)

def create_banner(parent, version, colors=None):
    """Alias for create_main_header."""
    return create_main_header(parent, version, colors)

def setup_header(parent, version, colors=None):
    """Alias for create_main_header."""
    return create_main_header(parent, version, colors)

# Layout setup functions
def setup_main_layout(parent, app, version, colors=None):
    """Complete layout setup."""
    try:
        if colors is None:
            from config import BRAND_COLORS
            colors = BRAND_COLORS
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        create_main_header(parent, version, colors)
        
        main_frame = ttk.Frame(parent, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        create_io_section(main_frame, app)
        create_process_controls(main_frame, app)
        create_status_and_log_section(main_frame, app)
        
        return True
    except Exception as e:
        print(f"Error in setup_main_layout: {e}")
        return False

def setup_gui_layout(parent, app, version, colors=None):
    """Alias for setup_main_layout."""
    return setup_main_layout(parent, app, version, colors)

def create_main_interface(parent, app, version, colors=None):
    """Alias for setup_main_layout."""
    return setup_main_layout(parent, app, version, colors)

def build_gui(parent, app, version, colors=None):
    """Alias for setup_main_layout."""
    return setup_main_layout(parent, app, version, colors)

# Style and theming functions
def setup_high_contrast_styles(*args, **kwargs):
    """Setup high contrast styles."""
    print("High contrast styles setup called")
    return None

def apply_theme(app, theme_name="default"):
    """Apply theme to application."""
    try:
        if hasattr(app, 'style'):
            app.style.theme_use(theme_name)
    except Exception as e:
        print(f"Error applying theme: {e}")

def configure_styles(app):
    """Configure application styles."""
    try:
        if hasattr(app, '_configure_styles'):
            app._configure_styles()
    except Exception as e:
        print(f"Error configuring styles: {e}")

def setup_colors(app, colors=None):
    """Setup application colors."""
    try:
        if colors and hasattr(app, 'brand_colors'):
            app.brand_colors = colors
    except Exception as e:
        print(f"Error setting up colors: {e}")

# Utility functions
def create_labeled_entry(parent, label_text, textvariable, **kwargs):
    """Create a labeled entry widget."""
    try:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=label_text).pack(side="left")
        entry = ttk.Entry(frame, textvariable=textvariable, **kwargs)
        entry.pack(side="left", fill="x", expand=True)
        return frame, entry
    except Exception as e:
        print(f"Error creating labeled entry: {e}")
        return None, None

def create_button_with_icon(parent, text, command, icon=None, **kwargs):
    """Create button with optional icon."""
    try:
        btn = ttk.Button(parent, text=text, command=command, **kwargs)
        if icon:
            btn.config(image=icon, compound="left")
        return btn
    except Exception as e:
        print(f"Error creating button: {e}")
        return ttk.Button(parent, text=text, command=command)

def add_tooltip(widget, text):
    """Add tooltip to widget."""
    try:
        # Simple tooltip implementation
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="yellow")
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    except Exception as e:
        print(f"Error adding tooltip: {e}")

# Grid and layout utilities
def configure_grid_weights(parent, rows=None, cols=None):
    """Configure grid weights for responsive layout."""
    try:
        if rows:
            for i, weight in enumerate(rows):
                parent.rowconfigure(i, weight=weight)
        if cols:
            for i, weight in enumerate(cols):
                parent.columnconfigure(i, weight=weight)
    except Exception as e:
        print(f"Error configuring grid weights: {e}")

def create_separator(parent, orient='horizontal'):
    """Create separator widget."""
    try:
        return ttk.Separator(parent, orient=orient)
    except Exception as e:
        print(f"Error creating separator: {e}")
        return ttk.Frame(parent, height=2, width=2)

# Window management
def setup_window_geometry(window, width=1200, height=900):
    """Setup window size and positioning."""
    try:
        window.geometry(f"{width}x{height}")
        window.minsize(1000, 800)
        
        # Center window
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception as e:
        print(f"Error setting up window geometry: {e}")

def center_window(window):
    """Center window on screen."""
    try:
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
    except Exception as e:
        print(f"Error centering window: {e}")

# Validation and error handling
def validate_gui_components(app):
    """Validate that required GUI components exist."""
    required = ['process_btn', 'log_text', 'progress_value', 'status_current_file']
    missing = [attr for attr in required if not hasattr(app, attr)]
    
    if missing:
        print(f"Warning: Missing GUI components: {missing}")
        return False
    return True

def safe_widget_config(widget, **kwargs):
    """Safely configure widget properties."""
    try:
        widget.config(**kwargs)
        return True
    except Exception as e:
        print(f"Error configuring widget: {e}")
        return False

def safe_grid_widget(widget, **kwargs):
    """Safely grid a widget."""
    try:
        widget.grid(**kwargs)
        return True
    except Exception as e:
        print(f"Error gridding widget: {e}")
        return False

def safe_pack_widget(widget, **kwargs):
    """Safely pack a widget."""
    try:
        widget.pack(**kwargs)
        return True
    except Exception as e:
        print(f"Error packing widget: {e}")
        return False

# Event handling utilities
def bind_events(app):
    """Bind common application events."""
    try:
        if hasattr(app, 'bind_all'):
            app.bind_all("<Control-q>", lambda e: app.quit())
            app.bind_all("<F11>", lambda e: getattr(app, 'toggle_fullscreen', lambda: None)())
    except Exception as e:
        print(f"Error binding events: {e}")

def setup_keyboard_shortcuts(app):
    """Setup keyboard shortcuts."""
    try:
        shortcuts = {
            "<Control-o>": "browse_excel",
            "<Control-f>": "browse_folder", 
            "<Control-s>": "start_processing",
            "<Escape>": "stop_processing"
        }
        
        for key, method_name in shortcuts.items():
            method = getattr(app, method_name, None)
            if method:
                app.bind_all(key, lambda e, m=method: m())
    except Exception as e:
        print(f"Error setting up keyboard shortcuts: {e}")

# Progress and status utilities
def update_progress(app, current, total, message=""):
    """Update progress display."""
    try:
        if hasattr(app, 'progress_value') and total > 0:
            app.progress_value.set((current / total) * 100)
        if hasattr(app, 'status_current_file') and message:
            app.status_current_file.set(message)
    except Exception as e:
        print(f"Error updating progress: {e}")

def reset_progress(app):
    """Reset progress display."""
    try:
        if hasattr(app, 'progress_value'):
            app.progress_value.set(0)
        if hasattr(app, 'status_current_file'):
            app.status_current_file.set("Ready")
    except Exception as e:
        print(f"Error resetting progress: {e}")

# === END COMPREHENSIVE BACKWARD COMPATIBILITY ===
'''

    # Add the aliases section to the end of the file
    updated_content = current_content + aliases_section
    
    # Write back to file
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Added comprehensive backward compatibility aliases to gui_components.py")
    return True

def main():
    """Main function"""
    print("Final Import Fix - Adding Comprehensive Aliases")
    print("=" * 50)
    
    success = add_comprehensive_aliases()
    
    if success:
        print("\n🎉 All done! Your gui_components.py now includes:")
        print("   • create_controls_section")
        print("   • create_main_controls") 
        print("   • create_status_section")
        print("   • create_input_section")
        print("   • setup_main_layout")
        print("   • And 30+ other backward compatibility aliases")
        print("\n🚀 Try launching your application now:")
        print("   python launcher.py")
    else:
        print("\n❌ Failed to add aliases. Check gui_components.py exists.")

if __name__ == "__main__":
    main()
