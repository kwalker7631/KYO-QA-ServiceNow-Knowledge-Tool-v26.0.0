# kyo_qa_tool_app.py - Fixed version with robust error handling
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue
import time
import importlib
import sys
import traceback

from config import BRAND_COLORS, ASSETS_DIR
from processing_engine import run_processing_job
from file_utils import open_file, ensure_folders, cleanup_temp_files
from version import get_version
import logging_utils

# Import GUI components with fallback
try:
    from gui_components import (
        create_main_header, create_io_section,
        create_process_controls, create_status_and_log_section
    )
    GUI_COMPONENTS_AVAILABLE = True
except ImportError:
    GUI_COMPONENTS_AVAILABLE = False
    print("Warning: gui_components.py not available, using fallback GUI")

# Import review tool with fallback
try:
    from kyo_review_tool import ReviewWindow
    REVIEW_TOOL_AVAILABLE = True
except ImportError:
    REVIEW_TOOL_AVAILABLE = False
    print("Warning: kyo_review_tool.py not available, pattern management disabled")

logger = logging_utils.setup_logger("app")

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize all variables first to prevent AttributeError
        self._init_variables()
        
        try:
            # Setup window and styles
            self._setup_window_styles()
            
            # Load icons safely (with fallbacks)
            self._load_icons_safely()
            
            # Create the GUI
            self._create_widgets()
            
            # Initialize application state
            self._init_application()
            
        except Exception as e:
            self._handle_startup_error(e)

    def _init_variables(self):
        """Initialize all instance variables to prevent AttributeError"""
        # Counter variables
        self.count_pass = tk.IntVar(value=0)
        self.count_fail = tk.IntVar(value=0)
        self.count_review = tk.IntVar(value=0)
        self.count_ocr = tk.IntVar(value=0)
        self.count_needs_review = self.count_review

        # Processing state
        self.is_processing = False
        self.is_paused = False
        self.result_file_path = None
        self.reviewable_files = []
        self.start_time = None
        self.last_run_info = {}
        
        # Threading
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        
        # User selections
        self.selected_folder = tk.StringVar()
        self.selected_excel = tk.StringVar()
        self.selected_files_list = []
        
        # UI state
        self.status_current_file = tk.StringVar(value="Ready to process")
        self.progress_value = tk.DoubleVar(value=0)
        self.time_remaining_var = tk.StringVar(value="")
        self.led_status_var = tk.StringVar(value="●")
        self.is_fullscreen = True

        # Icons (will be loaded safely)
        self.start_icon = None
        self.pause_icon = None
        self.stop_icon = None
        self.rerun_icon = None
        self.open_icon = None
        self.browse_icon = None
        self.patterns_icon = None
        self.exit_icon = None
        self.fullscreen_icon = None

    def _load_icons_safely(self):
        """Load icons with fallbacks for missing files"""
        icon_files = {
            'start_icon': 'start.png',
            'pause_icon': 'pause.png',
            'stop_icon': 'stop.png',
            'rerun_icon': 'rerun.png',
            'open_icon': 'open.png',
            'browse_icon': 'browse.png',
            'patterns_icon': 'patterns.png',
            'exit_icon': 'exit.png',
            'fullscreen_icon': 'fullscreen.png'
        }
        
        for attr_name, filename in icon_files.items():
            try:
                icon_path = ASSETS_DIR / filename
                if icon_path.exists():
                    setattr(self, attr_name, tk.PhotoImage(file=icon_path))
                    print(f"✓ Loaded icon: {filename}")
                else:
                    setattr(self, attr_name, None)
                    print(f"⚠ Icon not found: {filename} (will use text-only buttons)")
            except Exception as e:
                setattr(self, attr_name, None)
                print(f"⚠ Error loading icon {filename}: {e}")

    def _setup_window_styles(self):
        """Setup window properties and styles"""
        try:
            version = get_version()
            self.title(f"Kyocera QA Knowledge Tool v{version}")
            self.geometry("1200x900")
            self.minsize(1000, 800)

            # Try to set icon
            try:
                icon_path = Path(__file__).parent / "icon.ico"
                if icon_path.exists():
                    self.iconbitmap(icon_path)
            except Exception:
                pass  # Icon not critical
            
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.configure(bg=BRAND_COLORS["background"])
            self.columnconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            # Setup styles
            self.style = ttk.Style(self)
            self._configure_styles()
            
        except Exception as e:
            print(f"Warning: Style setup failed: {e}")
            # Continue without custom styles

    def _configure_styles(self):
        """Configure TTK styles with error handling"""
        try:
            self.style.theme_use("clam")
            
            # Basic styles
            self.style.configure("TFrame", background=BRAND_COLORS["background"])
            self.style.configure("Header.TFrame", background=BRAND_COLORS["frame_background"])
            self.style.configure("TLabel", background=BRAND_COLORS["background"], font=("Segoe UI", 10))
            self.style.configure("TLabelFrame", background=BRAND_COLORS["background"], borderwidth=1, relief="groove")
            self.style.configure("TLabelFrame.Label", background=BRAND_COLORS["background"], font=("Segoe UI", 11, "bold"))
            
            # Progress bar
            self.style.configure("Blue.Horizontal.TProgressbar", background=BRAND_COLORS["accent_blue"])
            
            # Treeview
            self.style.configure("Treeview", font=("Segoe UI", 9), fieldbackground=BRAND_COLORS["frame_background"])
            self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

            # Entry fields
            self.style.configure("TEntry", fieldbackground=BRAND_COLORS["frame_background"], borderwidth=1, relief="solid")
            self.style.map("TEntry",
                bordercolor=[("focus", BRAND_COLORS["highlight_blue"]), ('!focus', 'grey')],
                lightcolor=[("focus", BRAND_COLORS["highlight_blue"])],
                darkcolor=[("focus", BRAND_COLORS["highlight_blue"])]
            )

            # Buttons
            self.style.configure("TButton", font=("Segoe UI", 10), padding=6, relief="raised")
            self.style.map("TButton", 
                background=[('active', '#e0e0e0'), ('!active', '#f0f0f0')], 
                foreground=[('active', 'black'), ('!active', 'black')]
            )
            
            # Red button (for START)
            self.style.configure("Red.TButton", font=("Segoe UI", 12, "bold"), foreground="white")
            self.style.map("Red.TButton", 
                background=[('active', '#A81F14'), ('!active', BRAND_COLORS["kyocera_red"])], 
                foreground=[('active', 'white'), ('!active', 'white')]
            )

            # Status styles
            self.style.configure("Status.TFrame", background=BRAND_COLORS["status_default_bg"], relief="sunken", borderwidth=1)
            self.style.configure("Status.TLabel", font=("Segoe UI", 10))
            self.style.configure("Status.Header.TLabel", font=("Segoe UI", 10, "bold"))
            self.style.configure("LED.TLabel", font=("Segoe UI", 16))
            
            # Counter styles
            self.style.configure("Count.Green.TLabel", foreground=BRAND_COLORS["success_green"], font=("Segoe UI", 10, "bold"))
            self.style.configure("Count.Red.TLabel", foreground=BRAND_COLORS["fail_red"], font=("Segoe UI", 10, "bold"))
            self.style.configure("Count.Orange.TLabel", foreground=BRAND_COLORS["warning_orange"], font=("Segoe UI", 10, "bold"))
            self.style.configure("Count.Blue.TLabel", foreground=BRAND_COLORS["accent_blue"], font=("Segoe UI", 10, "bold"))
            
        except Exception as e:
            print(f"Warning: Some styles could not be configured: {e}")

    def _create_widgets(self):
        """Create the main GUI widgets"""
        try:
            if GUI_COMPONENTS_AVAILABLE:
                # Use modular components
                version = get_version()
                create_main_header(self, version, BRAND_COLORS)
                
                main_frame = ttk.Frame(self, padding=20)
                main_frame.grid(row=1, column=0, sticky="nsew")
                main_frame.columnconfigure(0, weight=1)
                main_frame.rowconfigure(2, weight=1)
                
                create_io_section(main_frame, self)
                create_process_controls(main_frame, self)
                create_status_and_log_section(main_frame, self)
                
                # Configure log text tags
                self._configure_log_tags()
            else:
                # Fallback to basic GUI
                self._create_basic_gui()
                
        except Exception as e:
            print(f"Error creating widgets: {e}")
            self._create_emergency_gui()

    def _create_basic_gui(self):
        """Create a basic GUI when gui_components is not available"""
        # Header
        header_frame = ttk.Frame(self, padding=10)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        version = get_version()
        ttk.Label(header_frame, text=f"KYO QA Tool v{version}", 
                 font=("Arial", 16, "bold")).pack()

        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding=10)
        file_frame.grid(row=0, column=0, sticky="ew", pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Excel File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_excel).grid(row=0, column=2)

        ttk.Label(file_frame, text="PDF Folder:").grid(row=1, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_folder).grid(row=1, column=2)

        # Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.grid(row=1, column=0, sticky="ew", pady=5)

        self.process_btn = ttk.Button(control_frame, text="START", command=self.start_processing, style="Red.TButton")
        self.process_btn.pack(side="left", padx=5)

        self.pause_btn = ttk.Button(control_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side="left", padx=5)

        # Progress
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.grid(row=2, column=0, sticky="ew", pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        # Status display
        ttk.Label(progress_frame, textvariable=self.status_current_file).grid(row=1, column=0, sticky="w")

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=log_scroll.set)

        # Initialize review tree placeholder
        self.review_tree = None
        self.review_file_btn = None

    def _create_emergency_gui(self):
        """Create minimal emergency GUI if everything else fails"""
        tk.Label(self, text="KYO QA Tool - Emergency Mode", 
                font=("Arial", 16), fg="red").pack(pady=20)
        
        tk.Label(self, text="GUI creation failed. Check console for errors.").pack()
        
        tk.Button(self, text="Exit", command=self.on_closing).pack(pady=10)

    def _configure_log_tags(self):
        """Configure text tags for log display"""
        try:
            self.log_text_tags = {
                "info": ("#00529B", "white"), 
                "warning": ("#9F6000", "#FEEFB3"),
                "error": ("#D8000C", "#FFD2D2"), 
                "success": ("#4F8A10", "#DFF2BF")
            }

            self.log_text.tag_configure("timestamp", foreground="grey")
            for tag, (fg, bg) in self.log_text_tags.items():
                self.log_text.tag_configure(f"{tag}_fg", foreground=fg)
                self.log_text.tag_configure(f"{tag}_line", background=bg, 
                                          selectbackground=BRAND_COLORS["highlight_blue"])
        except Exception as e:
            print(f"Warning: Could not configure log tags: {e}")

    def _init_application(self):
        """Initialize application state"""
        try:
            ensure_folders()
            self.attributes("-fullscreen", self.is_fullscreen)
            self.bind_all("<Escape>", self.toggle_fullscreen)
            self.after(100, self.process_response_queue)
            self.set_led("Ready")
            
            self.log_message("KYO QA Tool started successfully!", "success")
            
        except Exception as e:
            self.log_message(f"Warning during initialization: {e}", "warning")

    def _handle_startup_error(self, error):
        """Handle startup errors gracefully"""
        print(f"Startup error: {error}")
        traceback.print_exc()
        
        # Create minimal error display
        self.title("KYO QA Tool - Startup Error")
        self.geometry("600x400")
        
        error_frame = tk.Frame(self, bg="white")
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(error_frame, text="KYO QA Tool - Startup Error", 
                font=("Arial", 16, "bold"), fg="red", bg="white").pack(pady=10)
        
        error_text = tk.Text(error_frame, wrap=tk.WORD, height=15)
        error_text.pack(fill="both", expand=True)
        
        error_text.insert(tk.END, f"Error during startup:\n{error}\n\n")
        error_text.insert(tk.END, "Troubleshooting steps:\n")
        error_text.insert(tk.END, "1. Check that all required packages are installed\n")
        error_text.insert(tk.END, "2. Run: pip install -r requirements.txt\n")
        error_text.insert(tk.END, "3. Ensure the assets/ folder exists or is optional\n")
        error_text.insert(tk.END, "4. Check file permissions in the project directory\n")
        
        tk.Button(error_frame, text="Exit", command=self.destroy).pack(pady=10)

    # Safe versions of core methods with error handling
    def log_message(self, message, level="info"):
        """Add a message to the log with error handling"""
        try:
            if hasattr(self, 'log_text'):
                timestamp = time.strftime("%H:%M:%S")
                self.log_text.config(state=tk.NORMAL)
                start_index = self.log_text.index(tk.END)
                self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
                self.log_text.insert(tk.END, f"{message}\n", f"{level}_fg")
                end_index = self.log_text.index(tk.END)
                
                if level in ["warning", "error", "success"] and hasattr(self, 'log_text_tags'):
                    self.log_text.tag_add(f"{level}_line", start_index, end_index)
                
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            else:
                print(f"[{level.upper()}] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")
            print(f"Original message: [{level}] {message}")

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode safely"""
        try:
            self.is_fullscreen = not self.is_fullscreen
            self.attributes("-fullscreen", self.is_fullscreen)
        except Exception as e:
            self.log_message(f"Error toggling fullscreen: {e}", "warning")
        return "break"

    def start_processing(self, job=None, is_rerun=False):
        """Start processing with error handling"""
        try:
            if self.is_processing: 
                return
                
            if not job:
                input_path = self.selected_folder.get() or self.selected_files_list
                if not input_path:
                    messagebox.showwarning("Input Missing", "Please select files or a folder.")
                    return
                excel_path = self.selected_excel.get()
                if not excel_path:
                    messagebox.showwarning("Input Missing", "Please select a base Excel file.")
                    return
                job = {"excel_path": excel_path, "input_path": input_path}
                self.last_run_info = job
                
            job["is_rerun"] = is_rerun
            self.update_ui_for_start()
            self.log_message("Starting processing job...", "info")
            self.start_time = time.time()
            
            threading.Thread(
                target=run_processing_job, 
                args=(job, self.response_queue, self.cancel_event, self.pause_event), 
                daemon=True
            ).start()
            
        except Exception as e:
            self.log_message(f"Error starting processing: {e}", "error")
            self.update_ui_for_finish("Error")

    def browse_excel(self):
        """Browse for Excel file with error handling"""
        try:
            path = filedialog.askopenfilename(
                title="Select Excel Template", 
                filetypes=[("Excel Files", "*.xlsx *.xlsm"), ("All Files", "*.*")]
            )
            if path:
                self.selected_excel.set(path)
                self.log_message(f"Excel selected: {Path(path).name}", "info")
        except Exception as e:
            self.log_message(f"Error selecting Excel file: {e}", "error")

    def browse_folder(self):
        """Browse for folder with error handling"""
        try:
            path = filedialog.askdirectory(title="Select Folder with PDFs")
            if path:
                self.selected_folder.set(path)
                self.selected_files_list = []
                pdf_count = len(list(Path(path).glob("*.pdf")))
                if hasattr(self, 'files_label'):
                    self.files_label.config(text=f"{pdf_count} PDFs in folder")
                self.log_message(f"Folder selected: {path} ({pdf_count} PDFs)", "info")
        except Exception as e:
            self.log_message(f"Error selecting folder: {e}", "error")

    def browse_files(self):
        """Browse for individual files with error handling"""
        try:
            paths = filedialog.askopenfilenames(
                title="Select PDF Files", 
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
            )
            if paths:
                self.selected_files_list = list(paths)
                self.selected_folder.set("")
                if hasattr(self, 'files_label'):
                    self.files_label.config(text=f"{len(paths)} files selected")
                self.log_message(f"{len(paths)} PDF files selected", "info")
        except Exception as e:
            self.log_message(f"Error selecting files: {e}", "error")

    def toggle_pause(self):
        """Toggle pause state with error handling"""
        try:
            if not self.is_processing: 
                return
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_event.set()
                self.pause_btn.config(text=" Resume")
            else:
                self.pause_event.clear()
                self.pause_btn.config(text=" Pause")
            self.log_message("Processing paused" if self.is_paused else "Processing resumed", 
                           "warning" if self.is_paused else "info")
            self.set_led("Paused" if self.is_paused else "Processing")
        except Exception as e:
            self.log_message(f"Error toggling pause: {e}", "error")

    def stop_processing(self):
        """Stop processing with error handling"""
        try:
            if not self.is_processing: 
                return
            if messagebox.askyesno("Confirm Stop", "Stop the current processing job?"):
                self.cancel_event.set()
                self.log_message("Stopping processing...", "warning")
                self.set_led("Stopping")
        except Exception as e:
            self.log_message(f"Error stopping processing: {e}", "error")

    def open_result(self):
        """Open result file with error handling"""
        try:
            if self.result_file_path and Path(self.result_file_path).exists():
                open_file(self.result_file_path)
                self.log_message(f"Opened result file: {Path(self.result_file_path).name}", "info")
            else:
                messagebox.showwarning("Not Found", "Result file not found or has been moved.")
        except Exception as e:
            self.log_message(f"Error opening result file: {e}", "error")

    def open_pattern_manager(self):
        """Open pattern manager with error handling"""
        try:
            if not REVIEW_TOOL_AVAILABLE:
                messagebox.showwarning("Not Available", 
                                     "Pattern manager is not available. Check if kyo_review_tool.py exists.")
                return
                
            dialog = tk.Toplevel(self)
            dialog.title("Select Pattern Type")
            dialog.geometry("300x150")
            dialog.transient(self)
            dialog.grab_set()
            
            x = (self.winfo_screenwidth() // 2) - 150
            y = (self.winfo_screenheight() // 2) - 75
            dialog.geometry(f"+{x}+{y}")
            
            ttk.Label(dialog, text="Which patterns do you want to manage?", 
                     font=("Segoe UI", 10)).pack(pady=20)
            
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)
            
            def open_review(pattern_name, label):
                dialog.destroy()
                file_info = self.reviewable_files[0] if self.reviewable_files else None
                ReviewWindow(self, pattern_name, label, file_info)
            
            ttk.Button(button_frame, text="Model Patterns", 
                      command=lambda: open_review("MODEL_PATTERNS", "Model Patterns")).pack(side="left", padx=10)
            ttk.Button(button_frame, text="QA Patterns", 
                      command=lambda: open_review("QA_NUMBER_PATTERNS", "QA Number Patterns")).pack(side="left", padx=10)
                      
        except Exception as e:
            self.log_message(f"Error opening pattern manager: {e}", "error")

    def rerun_flagged_job(self):
        """Rerun flagged files with error handling"""
        try:
            if not self.reviewable_files:
                messagebox.showwarning("No Files", "No files need re-running.")
                return
            if not self.result_file_path:
                messagebox.showerror("Error", "Previous result file not found.")
                return
            files = [item["pdf_path"] for item in self.reviewable_files]
            self.log_message(f"Re-running {len(files)} flagged files...", "info")
            self.start_processing(job={"excel_path": self.result_file_path, "input_path": files}, is_rerun=True)
        except Exception as e:
            self.log_message(f"Error rerunning flagged files: {e}", "error")

    def set_led(self, status):
        """Set LED status with error handling"""
        try:
            led_config = {
                "Ready": ("#107C10", BRAND_COLORS["status_default_bg"]),
                "Processing": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_processing_bg"]),
                "OCR": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_ocr_bg"]),
                "AI": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_ai_bg"]),
                "Paused": (BRAND_COLORS["warning_orange"], BRAND_COLORS["status_default_bg"]),
                "Stopping": (BRAND_COLORS["fail_red"], BRAND_COLORS["status_default_bg"]),
                "Error": (BRAND_COLORS["fail_red"], BRAND_COLORS["status_default_bg"]),
                "Complete": ("#107C10", BRAND_COLORS["status_default_bg"]),
                "Queued": ("grey", BRAND_COLORS["status_default_bg"]),
                "Saving": ("#107C10", BRAND_COLORS["status_default_bg"]),
            }
            
            if hasattr(self, 'led_label') and hasattr(self, 'status_frame') and hasattr(self, 'style'):
                color, bg_color = led_config.get(status, ("grey", BRAND_COLORS["status_default_bg"]))
                self.led_label.config(foreground=color)
                self.status_frame.config(style="Status.TFrame")
                self.style.configure("Status.TFrame", background=bg_color)
                
                for child in self.status_frame.winfo_children():
                    child.configure(style="Status.TLabel")
                self.style.configure("Status.TLabel", background=bg_color)
                
        except Exception as e:
            print(f"Error setting LED status: {e}")

    def update_ui_for_start(self):
        """Update UI for processing start with error handling"""
        try:
            self.is_processing = True
            self.is_paused = False
            self.cancel_event.clear()
            self.pause_event.clear()
            
            # Reset counters
            for var in [self.count_pass, self.count_fail, self.count_review, self.count_ocr]: 
                var.set(0)
            
            # Clear reviewable files
            self.reviewable_files.clear()
            if hasattr(self, 'review_tree') and self.review_tree:
                self.review_tree.delete(*self.review_tree.get_children())
            
            # Update button states
            if hasattr(self, 'process_btn'):
                self.process_btn.config(state=tk.DISABLED)
            if hasattr(self, 'pause_btn'):
                self.pause_btn.config(state=tk.NORMAL, text=" Pause")
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state=tk.NORMAL)
            if hasattr(self, 'review_btn'):
                self.review_btn.config(state=tk.DISABLED)
            if hasattr(self, 'open_result_btn'):
                self.open_result_btn.config(state=tk.DISABLED)
            if hasattr(self, 'exit_btn'):
                self.exit_btn.config(state=tk.DISABLED)
            if hasattr(self, 'rerun_btn'):
                self.rerun_btn.config(state=tk.DISABLED)
            if hasattr(self, 'review_file_btn'):
                self.review_file_btn.config(state=tk.DISABLED)
            
            # Update status
            self.status_current_file.set("Initializing...")
            self.time_remaining_var.set("Calculating...")
            self.progress_value.set(0)
            self.set_led("Processing")
            
        except Exception as e:
            self.log_message(f"Error updating UI for start: {e}", "error")

    def update_ui_for_finish(self, status):
        """Update UI for processing finish with error handling"""
        try:
            self.is_processing = False
            self.is_paused = False
            
            # Update button states
            if hasattr(self, 'process_btn'):
                self.process_btn.config(state=tk.NORMAL)
            if hasattr(self, 'pause_btn'):
                self.pause_btn.config(state=tk.DISABLED, text=" Pause")
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state=tk.DISABLED)
            if hasattr(self, 'exit_btn'):
                self.exit_btn.config(state=tk.NORMAL)
            if hasattr(self, 'review_btn'):
                self.review_btn.config(state=tk.NORMAL)
                
            if self.result_file_path and hasattr(self, 'open_result_btn'): 
                self.open_result_btn.config(state=tk.NORMAL)
            if self.reviewable_files and hasattr(self, 'rerun_btn'): 
                self.rerun_btn.config(state=tk.NORMAL)
            
            final_status = "Complete" if status == "Complete" else "Error"
            self.status_current_file.set(f"Job {status}")
            self.time_remaining_var.set("Done!")
            self.set_led(final_status)
            self.progress_value.set(100)
            
        except Exception as e:
            self.log_message(f"Error updating UI for finish: {e}", "error")

    def update_progress(self, current, total):
        """Update progress display with error handling"""
        try:
            if total > 0:
                percent = (current / total) * 100
                self.progress_value.set(percent)
                if self.start_time and current > 0:
                    elapsed = time.time() - self.start_time
                    rate = current / elapsed
                    remaining = (total - current) / rate if rate > 0 else 0
                    if remaining > 60: 
                        self.time_remaining_var.set(f"~{int(remaining/60)}m {int(remaining%60)}s left")
                    else: 
                        self.time_remaining_var.set(f"~{int(remaining)}s left")
        except Exception as e:
            print(f"Error updating progress: {e}")

    def open_review_for_selected_file(self):
        """Open review for selected file with error handling"""
        try:
            if not hasattr(self, 'review_tree') or not self.review_tree:
                messagebox.showwarning("Not Available", "Review tree not available.")
                return
                
            selection = self.review_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a file to review.")
                return
                
            item_id = selection[0]
            filename = self.review_tree.item(item_id, "values")[0]
            review_info = next((f for f in self.reviewable_files if f['filename'] == filename), None)
            
            if review_info and REVIEW_TOOL_AVAILABLE:
                ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
            else:
                messagebox.showerror("Error", "Could not find review information or review tool not available.")
                
        except Exception as e:
            self.log_message(f"Error opening review: {e}", "error")

    def process_response_queue(self):
        """Process response queue with error handling"""
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                mtype = msg.get("type")
                
                if mtype == "log":
                    self.log_message(msg.get("msg", ""), msg.get("tag", "info"))
                elif mtype == "status":
                    self.status_current_file.set(msg.get("msg", ""))
                    if "led" in msg: 
                        self.set_led(msg["led"])
                elif mtype == "progress": 
                    self.update_progress(msg.get("current", 0), msg.get("total", 1))
                elif mtype == "increment_counter":
                    var = getattr(self, f"count_{msg.get('counter')}", None)
                    if var: 
                        var.set(var.get() + 1)
                elif mtype == "file_complete":
                    var = getattr(self, f"count_{msg.get('status', '').lower().replace(' ', '_')}", None)
                    if var: 
                        var.set(var.get() + 1)
                elif mtype == "review_item":
                    data = msg.get("data", {})
                    self.reviewable_files.append(data)
                    if hasattr(self, 'review_tree') and self.review_tree:
                        self.review_tree.insert('', 'end', values=(data.get('filename', 'Unknown'),))
                elif mtype == "result_path": 
                    self.result_file_path = msg.get("path")
                elif mtype == "finish":
                    status = msg.get("status", "Complete")
                    elapsed = time.time() - self.start_time if self.start_time else 0
                    self.log_message(f"Job finished: {status} (Time: {int(elapsed/60)}m {int(elapsed%60)}s)", 
                                   "success" if status == "Complete" else "error")
                    self.update_ui_for_finish(status)
                    
        except queue.Empty: 
            pass
        except Exception as e: 
            self.log_message(f"Error processing queue: {e}", "error")
        
        self.after(100, self.process_response_queue)

    def on_closing(self):
        """Handle application closing with error handling"""
        try:
            if self.is_processing:
                if not messagebox.askyesno("Exit", "A processing job is running. Are you sure you want to exit?"):
                    return

            print("Closing application...")
            self.cancel_event.set()
            cleanup_temp_files()
            self.destroy()
            
        except Exception as e:
            print(f"Error during closing: {e}")
            self.destroy()  # Force close

if __name__ == "__main__":
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
