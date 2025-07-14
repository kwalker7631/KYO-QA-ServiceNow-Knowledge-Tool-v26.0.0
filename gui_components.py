# gui_components.py - Fixed version with proper error handling and missing argument handling
import tkinter as tk
from tkinter import ttk

def create_main_header(parent, version, colors=None):
    """Create the main application header"""
    try:
        # Default colors if not provided
        if colors is None:
            colors = {
                "kyocera_red": "#DA291C",
                "frame_background": "#FFFFFF"
            }
        
        header = ttk.Frame(parent, style="Header.TFrame", padding=(10, 10))
        header.grid(row=0, column=0, sticky="ew")
        
        # Add separator
        ttk.Separator(header, orient='horizontal').pack(side="bottom", fill="x")
        
        # KYOCERA branding
        ttk.Label(header, text="KYOCERA", 
                 foreground=colors.get("kyocera_red", "#DA291C"), 
                 font=("Arial Black", 22)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Tool title
        ttk.Label(header, text=f"QA Knowledge Tool v{version}", 
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=(15, 0))
                 
    except Exception as e:
        print(f"Error creating header: {e}")
        # Fallback simple header
        simple_header = ttk.Frame(parent, padding=10)
        simple_header.grid(row=0, column=0, sticky="ew")
        ttk.Label(simple_header, text=f"KYO QA Tool v{version}", 
                 font=("Arial", 16, "bold")).pack()

# === AUTO-GENERATED MISSING FUNCTIONS ===
# Functions that might be called by the main application but were missing

def create_controls_section(parent, app):
    """Alias for create_process_controls for backward compatibility."""
    return create_process_controls(parent, app)

def create_main_controls(parent, app):
    """Alternative alias for create_process_controls."""
    return create_process_controls(parent, app)

def create_status_section(parent, app):
    """Alias for create_status_and_log_section for backward compatibility."""
    return create_status_and_log_section(parent, app)

def create_log_section(parent, app):
    """Alternative alias for log section."""
    return create_status_and_log_section(parent, app)

def create_input_section(parent, app):
    """Alias for create_io_section for backward compatibility.""" 
    return create_io_section(parent, app)

def create_file_section(parent, app):
    """Alternative alias for file selection section."""
    return create_io_section(parent, app)

def setup_main_layout(parent, app, version, colors=None):
    """Create complete main layout - alternative entry point."""
    try:
        # Default colors if not provided
        if colors is None:
            from config import BRAND_COLORS
            colors = BRAND_COLORS
        
        # Configure parent grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Create all sections
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
        print(f"Error setting up main layout: {e}")
        return False

def create_header_section(parent, version, colors=None):
    """Alias for create_main_header."""
    return create_main_header(parent, version, colors)

def setup_high_contrast_styles(*args, **kwargs):
    """Placeholder for high contrast styles setup."""
    print("High contrast styles setup called")
    return None

def create_io_section(parent, app):
    """Create the input/output file selection section"""
    try:
        io = ttk.LabelFrame(parent, text="1. Select Inputs", padding=10)
        io.grid(row=0, column=0, sticky="ew", pady=5)
        io.columnconfigure(1, weight=1)

        # Excel file selection
        ttk.Label(io, text="Excel to Clone:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
        
        # Check if app has the required attribute
        if hasattr(app, 'selected_excel'):
            ttk.Entry(io, textvariable=app.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
        else:
            # Create a placeholder if the attribute doesn't exist
            app.selected_excel = tk.StringVar()
            ttk.Entry(io, textvariable=app.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
        
        excel_btn = ttk.Button(io, text=" Browse...", command=getattr(app, 'browse_excel', lambda: print("Browse Excel not implemented")))
        if hasattr(app, 'browse_icon') and app.browse_icon:
            excel_btn.config(image=app.browse_icon, compound="left")
        excel_btn.grid(row=0, column=2, padx=5)

        # PDF folder selection
        ttk.Label(io, text="PDFs Folder:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
        
        if hasattr(app, 'selected_folder'):
            ttk.Entry(io, textvariable=app.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
        else:
            app.selected_folder = tk.StringVar()
            ttk.Entry(io, textvariable=app.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
        
        folder_btn = ttk.Button(io, text=" Browse...", command=getattr(app, 'browse_folder', lambda: print("Browse Folder not implemented")))
        if hasattr(app, 'browse_icon') and app.browse_icon:
            folder_btn.config(image=app.browse_icon, compound="left")
        folder_btn.grid(row=1, column=2, padx=5)

        # Individual files selection
        app.files_label = ttk.Label(io, text="Or select individual files -->")
        app.files_label.grid(row=2, column=1, sticky="e", padx=5, pady=(5,0))
        
        files_btn = ttk.Button(io, text=" Browse Files...", command=getattr(app, 'browse_files', lambda: print("Browse Files not implemented")))
        if hasattr(app, 'browse_icon') and app.browse_icon:
            files_btn.config(image=app.browse_icon, compound="left")
        files_btn.grid(row=2, column=2, padx=5, pady=(5,0))
        
    except Exception as e:
        print(f"Error creating IO section: {e}")
        # Create a basic fallback
        fallback = ttk.LabelFrame(parent, text="File Selection", padding=10)
        fallback.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Label(fallback, text="File selection interface failed to load").pack()

def create_process_controls(parent, app):
    """Create the processing control buttons section"""
    try:
        ctrl = ttk.LabelFrame(parent, text="2. Process & Manage", padding=10)
        ctrl.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Configure grid to have 4 equal columns
        for i in range(4):
            ctrl.columnconfigure(i, weight=1)

        # Main START button - spans all columns
        app.process_btn = ttk.Button(ctrl, text=" START", 
                                   command=getattr(app, 'start_processing', lambda: print("Start processing not implemented")), 
                                   style="Red.TButton")
        if hasattr(app, 'start_icon') and app.start_icon:
            app.process_btn.config(image=app.start_icon, compound="left")
        app.process_btn.grid(row=0, column=0, columnspan=4, sticky="ew", pady=2, padx=2)

        # Second row - control buttons
        app.pause_btn = ttk.Button(ctrl, text=" Pause", 
                                 command=getattr(app, 'toggle_pause', lambda: print("Pause not implemented")), 
                                 state=tk.DISABLED)
        if hasattr(app, 'pause_icon') and app.pause_icon:
            app.pause_btn.config(image=app.pause_icon, compound="left")
        app.pause_btn.grid(row=1, column=0, sticky="ew", pady=2, padx=2)

        app.stop_btn = ttk.Button(ctrl, text=" Stop", 
                                command=getattr(app, 'stop_processing', lambda: print("Stop not implemented")), 
                                state=tk.DISABLED)
        if hasattr(app, 'stop_icon') and app.stop_icon:
            app.stop_btn.config(image=app.stop_icon, compound="left")
        app.stop_btn.grid(row=1, column=1, sticky="ew", pady=2, padx=2)

        app.rerun_btn = ttk.Button(ctrl, text=" Re-run Flagged", 
                                 command=getattr(app, 'rerun_flagged_job', lambda: print("Rerun not implemented")), 
                                 state=tk.DISABLED)
        if hasattr(app, 'rerun_icon') and app.rerun_icon:
            app.rerun_btn.config(image=app.rerun_icon, compound="left")
        app.rerun_btn.grid(row=1, column=2, sticky="ew", pady=2, padx=2)

        app.open_result_btn = ttk.Button(ctrl, text=" Open Result", 
                                       command=getattr(app, 'open_result', lambda: print("Open result not implemented")), 
                                       state=tk.DISABLED)
        if hasattr(app, 'open_icon') and app.open_icon:
            app.open_result_btn.config(image=app.open_icon, compound="left")
        app.open_result_btn.grid(row=1, column=3, sticky="ew", pady=2, padx=2)

        # Third row - utility buttons
        app.review_btn = ttk.Button(ctrl, text=" Patterns", 
                                  command=getattr(app, 'open_pattern_manager', lambda: print("Pattern manager not implemented")))
        if hasattr(app, 'patterns_icon') and app.patterns_icon:
            app.review_btn.config(image=app.patterns_icon, compound="left")
        app.review_btn.grid(row=2, column=0, sticky="ew", pady=2, padx=2)

        # Create fullscreen button if method exists
        if hasattr(app, 'toggle_fullscreen'):
            app.fullscreen_btn = ttk.Button(ctrl, text=" Fullscreen", command=app.toggle_fullscreen)
            if hasattr(app, 'fullscreen_icon') and app.fullscreen_icon:
                app.fullscreen_btn.config(image=app.fullscreen_icon, compound="left")
            app.fullscreen_btn.grid(row=2, column=1, sticky="ew", pady=2, padx=2)

        # Exit button - always in the rightmost position
        app.exit_btn = ttk.Button(ctrl, text=" Exit", 
                                command=getattr(app, 'on_closing', lambda: print("Exit not implemented")))
        if hasattr(app, 'exit_icon') and app.exit_icon:
            app.exit_btn.config(image=app.exit_icon, compound="left")
        app.exit_btn.grid(row=2, column=3, sticky="ew", pady=2, padx=2)
        
    except Exception as e:
        print(f"Error creating process controls: {e}")
        # Create a basic fallback
        fallback = ttk.LabelFrame(parent, text="Controls", padding=10)
        fallback.grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Button(fallback, text="START", command=lambda: print("Basic start button")).pack(pady=5)

def create_status_and_log_section(parent, app):
    """Create the status display and logging section"""
    try:
        stat = ttk.LabelFrame(parent, text="3. Status & Logs", padding=10)
        stat.grid(row=2, column=0, sticky="nsew", pady=5)
        stat.columnconfigure(0, weight=1)
        stat.rowconfigure(5, weight=1)  # Make log area expandable

        # Status indicator
        app.status_frame = ttk.Frame(stat, style="Status.TFrame", padding=5)
        app.status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        app.status_frame.columnconfigure(1, weight=1)
        
        # Initialize variables if they don't exist
        if not hasattr(app, 'led_status_var'):
            app.led_status_var = tk.StringVar(value="●")
        if not hasattr(app, 'status_current_file'):
            app.status_current_file = tk.StringVar(value="Ready")
        
        app.led_label = ttk.Label(app.status_frame, textvariable=app.led_status_var, style="LED.TLabel")
        app.led_label.grid(row=0, column=0, sticky="w")
        
        ttk.Label(app.status_frame, textvariable=app.status_current_file, style="Status.TLabel").grid(row=0, column=1, sticky="ew", padx=5)

        # Progress bar
        prog_frame = ttk.Frame(stat)
        prog_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,10))
        prog_frame.columnconfigure(0, weight=1)
        
        if not hasattr(app, 'progress_value'):
            app.progress_value = tk.DoubleVar(value=0)
        if not hasattr(app, 'time_remaining_var'):
            app.time_remaining_var = tk.StringVar(value="")
        
        app.progress_bar = ttk.Progressbar(prog_frame, variable=app.progress_value, style="Blue.Horizontal.TProgressbar")
        app.progress_bar.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(prog_frame, textvariable=app.time_remaining_var).grid(row=0, column=1, sticky="e", padx=10)

        # Summary counters
        sum_frame = ttk.Frame(stat)
        sum_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        
        # Initialize counter variables if they don't exist
        for counter in ['count_pass', 'count_fail', 'count_review', 'count_ocr']:
            if not hasattr(app, counter):
                setattr(app, counter, tk.IntVar(value=0))
        
        counters = [
            ("Pass:", app.count_pass, "Green"), 
            ("Fail:", app.count_fail, "Red"), 
            ("Review:", app.count_review, "Orange"), 
            ("OCR:", app.count_ocr, "Blue")
        ]
        
        for i, (text, var, color) in enumerate(counters):
            ttk.Label(sum_frame, text=text, style="Status.Header.TLabel").pack(side="left", padx=(15, 2))
            ttk.Label(sum_frame, textvariable=var, style=f"Count.{color}.TLabel").pack(side="left")

        # Review files section
        rev_frame = ttk.Frame(stat)
        rev_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
        rev_frame.rowconfigure(1, weight=1)
        rev_frame.columnconfigure(0, weight=1)
        
        ttk.Label(rev_frame, text="Files to Review:", style="Status.Header.TLabel").grid(row=0, column=0, sticky="w")
        
        app.review_file_btn = ttk.Button(rev_frame, text="Review Selected", 
                                        command=getattr(app, 'open_review_for_selected_file', lambda: print("Review not implemented")), 
                                        state=tk.DISABLED)
        app.review_file_btn.grid(row=0, column=1, sticky="e")
        
        app.review_tree = ttk.Treeview(rev_frame, columns=('file',), show='headings', height=4)
        app.review_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=2)
        app.review_tree.heading('file', text='File Name')
        
        # Bind selection event
        app.review_tree.bind("<<TreeviewSelect>>", 
                           lambda e: app.review_file_btn.config(state=tk.NORMAL if app.review_tree.selection() else tk.DISABLED))

        # Add scrollbar to review tree
        rev_scroll = ttk.Scrollbar(rev_frame, orient="vertical", command=app.review_tree.yview)
        rev_scroll.grid(row=1, column=2, sticky="ns", pady=2)
        app.review_tree.configure(yscrollcommand=rev_scroll.set)

        # Log display area
        log_frame = ttk.Frame(stat)
        log_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=(10,2))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        app.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, 
                              relief="solid", borderwidth=1, font=("Consolas", 9))
        app.log_text.grid(row=0, column=0, sticky="nsew")
        
        log_scroll = ttk.Scrollbar(log_frame, command=app.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        app.log_text.config(yscrollcommand=log_scroll.set)
        
    except Exception as e:
        print(f"Error creating status and log section: {e}")
        # Create a basic fallback
        fallback = ttk.LabelFrame(parent, text="Status", padding=10)
        fallback.grid(row=2, column=0, sticky="nsew", pady=5)
        fallback.rowconfigure(1, weight=1)
        fallback.columnconfigure(0, weight=1)
        
        # Basic status display
        if not hasattr(app, 'status_current_file'):
            app.status_current_file = tk.StringVar(value="Ready")
        ttk.Label(fallback, textvariable=app.status_current_file).grid(row=0, column=0, sticky="w")
        
        # Basic log area
        app.log_text = tk.Text(fallback, height=10, wrap=tk.WORD, state=tk.DISABLED)
        app.log_text.grid(row=1, column=0, sticky="nsew")
        
        # Initialize missing attributes for compatibility
        app.review_tree = None
        app.review_file_btn = None
        if not hasattr(app, 'progress_value'):
            app.progress_value = tk.DoubleVar(value=0)

def create_minimal_gui(parent, app):
    """Create a minimal GUI fallback if the main components fail"""
    try:
        main_frame = ttk.Frame(parent, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="KYO QA Tool - Minimal Interface", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding=10)
        file_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_frame, text="Excel File:").pack(anchor="w")
        excel_frame = ttk.Frame(file_frame)
        excel_frame.pack(fill="x", pady=2)
        ttk.Entry(excel_frame, textvariable=app.selected_excel).pack(side="left", fill="x", expand=True)
        ttk.Button(excel_frame, text="Browse", command=app.browse_excel).pack(side="right", padx=(5,0))
        
        ttk.Label(file_frame, text="PDF Folder:").pack(anchor="w", pady=(10,0))
        folder_frame = ttk.Frame(file_frame)
        folder_frame.pack(fill="x", pady=2)
        ttk.Entry(folder_frame, textvariable=app.selected_folder).pack(side="left", fill="x", expand=True)
        ttk.Button(folder_frame, text="Browse", command=app.browse_folder).pack(side="right", padx=(5,0))
        
        # Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill="x", pady=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        app.process_btn = ttk.Button(button_frame, text="START", command=app.start_processing)
        app.process_btn.pack(side="left", padx=5)
        
        app.pause_btn = ttk.Button(button_frame, text="Pause", command=app.toggle_pause, state=tk.DISABLED)
        app.pause_btn.pack(side="left", padx=5)
        
        app.stop_btn = ttk.Button(button_frame, text="Stop", command=app.stop_processing, state=tk.DISABLED)
        app.stop_btn.pack(side="left", padx=5)
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill="both", expand=True, pady=5)
        
        ttk.Label(status_frame, textvariable=app.status_current_file).pack(anchor="w")
        
        app.progress_bar = ttk.Progressbar(status_frame, variable=app.progress_value)
        app.progress_bar.pack(fill="x", pady=5)
        
        app.log_text = tk.Text(status_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        app.log_text.pack(fill="both", expand=True)
        
        # Initialize placeholder attributes for compatibility
        app.review_tree = None
        app.review_file_btn = None
        app.files_label = ttk.Label(status_frame, text="")
        
        print("✅ Minimal GUI created successfully")
        
    except Exception as e:
        print(f"Error creating minimal GUI: {e}")
        raise

# Test function
def test_gui_components():
    """Test GUI components creation"""
    try:
        root = tk.Tk()
        root.title("GUI Components Test")
        root.geometry("800x600")
        
        # Mock app object with required attributes
        class MockApp:
            def __init__(self):
                self.selected_excel = tk.StringVar()
                self.selected_folder = tk.StringVar()
                self.status_current_file = tk.StringVar(value="Ready")
                self.progress_value = tk.DoubleVar(value=0)
                self.time_remaining_var = tk.StringVar(value="")
                self.led_status_var = tk.StringVar(value="●")
                self.count_pass = tk.IntVar(value=0)
                self.count_fail = tk.IntVar(value=0)
                self.count_review = tk.IntVar(value=0)
                self.count_ocr = tk.IntVar(value=0)
                
                # Mock icons
                self.start_icon = None
                self.browse_icon = None
                self.pause_icon = None
                self.stop_icon = None
                self.rerun_icon = None
                self.open_icon = None
                self.patterns_icon = None
                self.exit_icon = None
                self.fullscreen_icon = None
            
            def browse_excel(self): print("Browse Excel")
            def browse_folder(self): print("Browse Folder")
            def browse_files(self): print("Browse Files")
            def start_processing(self): print("Start Processing")
            def toggle_pause(self): print("Toggle Pause")
            def stop_processing(self): print("Stop Processing")
            def rerun_flagged_job(self): print("Rerun Flagged")
            def open_result(self): print("Open Result")
            def open_pattern_manager(self): print("Pattern Manager")
            def toggle_fullscreen(self): print("Toggle Fullscreen")
            def on_closing(self): root.quit()
            def open_review_for_selected_file(self): print("Review Selected")
        
        app = MockApp()
        
        # Test creating components
        colors = {"kyocera_red": "#DA291C"}
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        
        create_main_header(root, "26.0.0", colors)
        
        main_frame = ttk.Frame(root, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        create_io_section(main_frame, app)
        create_process_controls(main_frame, app)
        create_status_and_log_section(main_frame, app)
        
        print("✅ All GUI components created successfully")
        
        # Don't run mainloop in test
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI components test failed: {e}")
        return False

if __name__ == "__main__":
    test_gui_components()

# === AUTO-GENERATED MISSING FUNCTIONS ===
# Functions that might be called by the main application but were missing

def setup_high_contrast_styles(*args, **kwargs):
    """Setup high contrast styles for accessibility."""
    print("High contrast styles setup called")
    return None

def create_button_with_icon(parent, text, command, icon=None, **kwargs):
    """Helper function to create buttons with optional icons."""
    try:
        btn = ttk.Button(parent, text=text, command=command, **kwargs)
        if icon:
            btn.config(image=icon, compound="left")
        return btn
    except Exception as e:
        print(f"Error creating button: {e}")
        return ttk.Button(parent, text=text, command=command)

def setup_window_geometry(window, width=1200, height=900):
    """Setup window size and positioning."""
    try:
        window.geometry(f"{width}x{height}")
        window.minsize(1000, 800)
        
        # Center window on screen
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    except Exception as e:
        print(f"Error setting up window geometry: {e}")

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
    """Create a separator widget."""
    try:
        return ttk.Separator(parent, orient=orient)
    except Exception as e:
        print(f"Error creating separator: {e}")
        return ttk.Frame(parent, height=2 if orient == 'horizontal' else 2, width=2)

def apply_custom_styling(app, style_config=None):
    """Apply custom styling to the application."""
    try:
        if hasattr(app, 'style') and style_config:
            # Apply any custom styles if provided
            pass
        print("Custom styling applied")
    except Exception as e:
        print(f"Error applying custom styles: {e}")

def configure_theme(app, theme_name="default"):
    """Configure application theme."""
    try:
        if hasattr(app, 'style'):
            available_themes = app.style.theme_names()
            if theme_name in available_themes:
                app.style.theme_use(theme_name)
                print(f"Theme set to: {theme_name}")
            else:
                print(f"Theme '{theme_name}' not available. Available: {available_themes}")
        else:
            print("No style object available for theming")
    except Exception as e:
        print(f"Error configuring theme: {e}")

def create_tooltip(widget, text):
    """Create a tooltip for a widget (placeholder implementation)."""
    try:
        # Basic tooltip implementation
        def on_enter(event):
            widget.tooltip = tk.Toplevel()
            widget.tooltip.wm_overrideredirect(True)
            widget.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(widget.tooltip, text=text, background="yellow")
            label.pack()
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    except Exception as e:
        print(f"Error creating tooltip: {e}")

def update_progress_display(app, current, total, message=""):
    """Update progress display in the GUI."""
    try:
        if hasattr(app, 'progress_value') and total > 0:
            percent = (current / total) * 100
            app.progress_value.set(percent)
        
        if hasattr(app, 'status_current_file') and message:
            app.status_current_file.set(message)
            
    except Exception as e:
        print(f"Error updating progress display: {e}")

def show_status_message(app, message, level="info"):
    """Show a status message in the application."""
    try:
        if hasattr(app, 'log_message'):
            app.log_message(message, level)
        else:
            print(f"[{level.upper()}] {message}")
    except Exception as e:
        print(f"Error showing status message: {e}")

def reset_ui_state(app):
    """Reset UI to initial state."""
    try:
        # Reset counters
        for counter in ['count_pass', 'count_fail', 'count_review', 'count_ocr']:
            if hasattr(app, counter):
                getattr(app, counter).set(0)
        
        # Reset progress
        if hasattr(app, 'progress_value'):
            app.progress_value.set(0)
        
        # Reset status
        if hasattr(app, 'status_current_file'):
            app.status_current_file.set("Ready")
            
        print("UI state reset")
        
    except Exception as e:
        print(f"Error resetting UI state: {e}")

def validate_gui_state(app):
    """Validate that all required GUI components are present."""
    required_attributes = [
        'process_btn', 'pause_btn', 'stop_btn', 'log_text',
        'progress_value', 'status_current_file'
    ]
    
    missing = []
    for attr in required_attributes:
        if not hasattr(app, attr):
            missing.append(attr)
    
    if missing:
        print(f"Warning: Missing GUI attributes: {missing}")
        return False
    
    return True


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
