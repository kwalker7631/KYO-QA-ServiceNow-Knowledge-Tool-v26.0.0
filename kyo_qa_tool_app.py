# kyo_qa_tool_app.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue
import time
import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app")

# Try to import from local modules with fallbacks
try:
    from version import VERSION
except ImportError:
    VERSION = "26.0.0"  # Fallback version

try:
    from config import BRAND_COLORS, ASSETS_DIR, OUTPUT_DIR
except ImportError:
    # Fallback configuration
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
    }
    ASSETS_DIR = Path(__file__).parent / "assets"
    OUTPUT_DIR = Path(__file__).parent / "output"

try:
    from processing_engine import run_processing_job
except ImportError:
    # Stub function if module is missing
    def run_processing_job(job_info, progress_queue, cancel_event, pause_event):
        progress_queue.put({"type": "log", "tag": "error", "msg": "processing_engine module not found"})
        progress_queue.put({"type": "finish", "status": "Error"})

try:
    from file_utils import open_file
except ImportError:
    # Fallback open_file function
    def open_file(path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{path}"')
        else:  # Linux and other Unix
            os.system(f'xdg-open "{path}"')

try:
    from kyo_review_tool import ReviewWindow
except ImportError:
    # Stub class if module is missing
    class ReviewWindow(tk.Toplevel):
        def __init__(self, parent, pattern_name, pattern_label, file_info=None):
            super().__init__(parent)
            self.title("Review Tool Not Available")
            tk.Label(self, text="The review tool module could not be loaded").pack(padx=20, pady=20)
            ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

# Ensure output directory exists
def ensure_output_dir():
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "needs_review").mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")

# Call this at startup
ensure_output_dir()

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Variable Declarations ---
        self.is_processing = False
        self.is_paused = False
        self.result_file_path = None
        self.review_files = []
        self.start_time = None
        self.last_run_info = {}
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.selected_folder = tk.StringVar()
        self.selected_excel = tk.StringVar()
        self.selected_files_list = []
        self.status_current_file = tk.StringVar(value="Ready to process")
        self.progress_value = tk.DoubleVar(value=0)
        self.progress_percent_var = tk.StringVar(value="0%")
        self.time_remaining_var = tk.StringVar(value="Time Remaining: N/A")
        self.stage_var = tk.StringVar(value="Ready")
        self.pass_count = tk.IntVar(value=0)
        self.fail_count = tk.IntVar(value=0)
        self.review_count = tk.IntVar(value=0)
        self.ocr_count = tk.IntVar(value=0)

        # --- UI Setup ---
        self.style = ttk.Style(self)
        self._setup_window_styles()
        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.process_response_queue)
        self.update_review_list()
        
        logger.info(f"Kyo QA Tool v{VERSION} initialized successfully.")

    def _setup_window_styles(self):
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1200x850")
        self.minsize(1100, 750)
        self.configure(bg="#F5F5F5")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1) # Allow the review section to expand
        
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            # If the theme doesn't exist, use default
            pass
            
        # Configure common styles
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("Header.TFrame", background="#232323")
        self.style.configure("Header.TLabel", background="#232323", foreground="white", font=("Segoe UI", 12, "bold"))
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        
        # Action button styles
        self.style.configure("Accent.TButton", foreground="white", background="#0078D4", font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#106EBE")])
        
        # Progress bar style
        self.style.configure("Horizontal.TProgressbar", background="#0078D4")

    def _create_widgets(self):
        # Main header
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(10, 5))
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        title_label = ttk.Label(header_frame, text=f"KYOCERA QA Knowledge Tool v{VERSION}", style="Header.TLabel")
        title_label.grid(row=0, column=0, sticky="w")
        
        # Input section
        input_frame = ttk.LabelFrame(self, text="1. Select Inputs", padding=(10, 5))
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Excel to Clone:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        excel_entry = ttk.Entry(input_frame, textvariable=self.selected_excel)
        excel_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        excel_browse_btn = ttk.Button(input_frame, text="Browse...", command=self.browse_excel)
        excel_browse_btn.grid(row=0, column=2, padx=5)

        ttk.Label(input_frame, text="PDFs Folder:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        folder_entry = ttk.Entry(input_frame, textvariable=self.selected_folder)
        folder_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        folder_browse_btn = ttk.Button(input_frame, text="Browse...", command=self.browse_folder)
        folder_browse_btn.grid(row=1, column=2, padx=5)
        
        ttk.Label(input_frame, text="Or select individual files ->").grid(row=1, column=3, sticky="w", padx=10)
        files_btn = ttk.Button(input_frame, text="Browse Files...", command=self.browse_files)
        files_btn.grid(row=1, column=4, padx=5)
        
        # Control section
        controls_frame = ttk.LabelFrame(self, text="2. Process & Manage", padding=(10, 5))
        controls_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        controls_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.start_btn = ttk.Button(controls_frame, text="START", command=self.start_processing, style="Accent.TButton")
        self.start_btn.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        self.pause_btn = ttk.Button(controls_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        self.stop_btn = ttk.Button(controls_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.rerun_btn = ttk.Button(controls_frame, text="Re-run Flagged", command=lambda: self.start_processing(is_rerun=True))
        self.rerun_btn.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        self.open_result_btn = ttk.Button(controls_frame, text="Open Result", command=self.open_result_file, state=tk.DISABLED)
        self.open_result_btn.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        self.patterns_btn = ttk.Button(controls_frame, text="Patterns", command=self.open_review_tool)
        self.patterns_btn.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        fullscreen_btn = ttk.Button(controls_frame, text="Fullscreen", command=self.toggle_fullscreen)
        fullscreen_btn.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        exit_btn = ttk.Button(controls_frame, text="Exit", command=self.on_closing)
        exit_btn.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
        
        # Status and log section
        status_frame = ttk.LabelFrame(self, text="3. Status & Logs", padding=(10, 5))
        status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        status_frame.columnconfigure(0, weight=1)
        
        # Progress Bar and Status
        prog_frame = ttk.Frame(status_frame)
        prog_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        prog_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_value, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(prog_frame, textvariable=self.progress_percent_var).grid(row=0, column=1, padx=(5, 10))
        self.cancel_progress_btn = ttk.Button(prog_frame, text="Cancel", command=self.stop_processing, width=8, state=tk.DISABLED)
        self.cancel_progress_btn.grid(row=0, column=2)
        
        # Status indicator with current file
        status_indicator = ttk.Frame(status_frame)
        status_indicator.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        status_indicator.columnconfigure(1, weight=1)
        
        self.status_dot_color = tk.StringVar(value="green")
        status_dot = tk.Label(status_indicator, text="●", foreground="green", font=("Segoe UI", 12))
        status_dot.grid(row=0, column=0, sticky="w", padx=(5, 0))
        ttk.Label(status_indicator, textvariable=self.status_current_file).grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Add processing stage indicator
        ttk.Label(status_indicator, text="Stage:").grid(row=0, column=2, padx=(20, 5))
        ttk.Label(status_indicator, textvariable=self.stage_var).grid(row=0, column=3, padx=(0, 20))
        
        # Counters
        counter_frame = ttk.Frame(status_frame)
        counter_frame.grid(row=1, column=4, sticky="e")
        ttk.Label(counter_frame, text="Pass:").pack(side="left", padx=(10, 2))
        ttk.Label(counter_frame, textvariable=self.pass_count).pack(side="left")
        ttk.Label(counter_frame, text="Fail:").pack(side="left", padx=(10, 2))
        ttk.Label(counter_frame, textvariable=self.fail_count).pack(side="left")
        ttk.Label(counter_frame, text="Review:").pack(side="left", padx=(10, 2))
        ttk.Label(counter_frame, textvariable=self.review_count).pack(side="left")
        ttk.Label(counter_frame, text="OCR:").pack(side="left", padx=(10, 2))
        ttk.Label(counter_frame, textvariable=self.ocr_count).pack(side="left")
        
        # Log text area
        log_frame = ttk.Frame(status_frame)
        log_frame.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=6, wrap="word", font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Review files section
        review_frame = ttk.LabelFrame(self, text="Files to Review", padding=(10, 5))
        review_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        review_frame.columnconfigure(0, weight=1)
        review_frame.rowconfigure(0, weight=1)
        
        self.review_listbox = tk.Listbox(review_frame, selectmode=tk.SINGLE)
        self.review_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(review_frame, orient="vertical", command=self.review_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.review_listbox.config(yscrollcommand=scrollbar.set)
        
        review_btn = ttk.Button(review_frame, text="Review Selected", command=self.review_selected_file)
        review_btn.grid(row=1, column=0, columnspan=2, sticky="e", pady=5)

    def start_processing(self, is_rerun=False):
        if self.is_processing:
            return
        
        if not is_rerun:
            # Check for input
            input_path = self.selected_files_list or self.selected_folder.get()
            if not input_path:
                messagebox.showwarning("Input Missing", "Please select a folder or files to process.")
                return
                
            excel_path = self.selected_excel.get()
            if not excel_path:
                messagebox.showwarning("Input Missing", "Please select a base Excel file.")
                return
            
            # Count files to process
            file_count = 0
            if isinstance(input_path, list):
                file_count = len(input_path)
            else:
                try:
                    folder = Path(input_path)
                    if folder.exists():
                        file_count = len([f for f in folder.glob('*.pdf')])
                    else:
                        messagebox.showwarning("Invalid Path", "The selected folder does not exist.")
                        return
                except Exception as e:
                    self.log_message(f"Error counting files: {e}", "error")
                    return
            
            # Confirm if processing many files
            if file_count > 30:
                if not messagebox.askyesno("Confirm Processing", 
                                           f"You are about to process {file_count} files, which may take some time.\n\nDo you want to continue?"):
                    return
                    
            job = {
                "excel_path": excel_path,
                "input_path": input_path,
                "output_dir": Path(excel_path).parent,
                "is_rerun": False
            }
            self.last_run_info = job
        else:
            # Re-run using files in the needs_review folder
            if not self.result_file_path:
                messagebox.showwarning("No Previous Run", "There is no previous run to re-run.")
                return
                
            # Check if there are review files
            review_files = self.get_review_files()
            if not review_files:
                messagebox.showinfo("No Files to Review", "There are no files that need review.")
                return
                
            job = {
                "excel_path": self.result_file_path,
                "input_path": review_files,
                "output_dir": Path(self.result_file_path).parent,
                "is_rerun": True
            }
            
        self.update_ui_for_start()
        target_desc = "flagged files" if is_rerun else (Path(self.selected_folder.get()).name if self.selected_folder.get() else f"{len(self.selected_files_list)} files")
        self.log_message(f"Starting job for: {target_desc}", "info")
        
        threading.Thread(target=run_processing_job, 
                         args=(job, self.response_queue, self.cancel_event, self.pause_event), 
                         daemon=True).start()

    def browse_excel(self):
        path = filedialog.askopenfilename(
            title="Select Excel Template", 
            filetypes=[("Excel Files", "*.xlsx *.xlsm"), ("All Files", "*.*")]
        )
        if path:
            self.selected_excel.set(path)
            self.log_message(f"Selected Excel file: {Path(path).name}", "info")

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_folder.set(path)
            self.selected_files_list = []
            
            # Count PDFs in the folder
            try:
                pdf_count = len(list(Path(path).glob("*.pdf")))
                self.log_message(f"Selected folder: {path} with {pdf_count} PDF files", "info")
            except Exception as e:
                self.log_message(f"Error reading folder: {e}", "error")

    def browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF Files", 
            filetypes=[("PDF Files", "*.pdf"), ("ZIP Archives", "*.zip")]
        )
        if paths:
            self.selected_files_list = list(paths)
            self.selected_folder.set(f"{len(paths)} files selected")
            self.log_message(f"Selected {len(paths)} files for processing", "info")

    def on_closing(self):
        if self.is_processing and not messagebox.askyesno("Exit", "Processing is running. Are you sure?"):
            return
        self.cancel_event.set()
        self.destroy()

    def process_response_queue(self):
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "finish":
                    self.update_ui_for_finish(msg.get("status", "Complete"))
                elif msg_type == "status":
                    self.status_current_file.set(msg.get("msg"))
                    if "stage" in msg:
                        self.stage_var.set(msg.get("stage"))
                elif msg_type == "progress":
                    value = msg.get("value", 0)
                    self.progress_value.set(value)
                    self.progress_percent_var.set(f"{int(value)}%")
                    
                    # Calculate time remaining
                    if self.start_time and value > 0:
                        elapsed = time.time() - self.start_time
                        if elapsed > 0:
                            estimated_total = elapsed * 100 / value
                            remaining = estimated_total - elapsed
                            mins, secs = divmod(int(remaining), 60)
                            if mins > 0:
                                self.time_remaining_var.set(f"Time Remaining: ~{mins}m {secs}s")
                            else:
                                self.time_remaining_var.set(f"Time Remaining: ~{secs}s")
                elif msg_type == "result_path":
                    self.result_file_path = msg.get("path")
                    self.open_result_btn.config(state=tk.NORMAL)
                elif msg_type == "update_counts":
                    if "pass" in msg:
                        self.pass_count.set(msg.get("pass"))
                    if "fail" in msg:
                        self.fail_count.set(msg.get("fail"))
                    if "review" in msg:
                        self.review_count.set(msg.get("review"))
                    if "ocr" in msg:
                        self.ocr_count.set(msg.get("ocr"))
                elif msg_type == "file_complete":
                    status = msg.get("status", "").lower()
                    if status == "pass":
                        self.pass_count.set(self.pass_count.get() + 1)
                    elif status == "fail":
                        self.fail_count.set(self.fail_count.get() + 1)
                    elif status == "needs review":
                        self.review_count.set(self.review_count.get() + 1)
                elif msg_type == "increment_counter":
                    counter = msg.get("counter", "")
                    if counter == "pass":
                        self.pass_count.set(self.pass_count.get() + 1)
                    elif counter == "fail":
                        self.fail_count.set(self.fail_count.get() + 1)
                    elif counter == "review":
                        self.review_count.set(self.review_count.get() + 1)
                    elif counter == "ocr":
                        self.ocr_count.set(self.ocr_count.get() + 1)
                elif msg_type == "review_item":
                    self.review_files.append(msg.get("data", {}))
                    filename = msg.get("data", {}).get("filename", "Unknown")
                    self.review_listbox.insert(tk.END, filename)
                elif msg_type == "log":
                    self.log_message(msg.get("msg", ""), msg.get("tag", "info"))

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_response_queue)

    def update_ui_for_start(self):
        self.is_processing = True
        self.start_time = time.time()
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.cancel_progress_btn.config(state=tk.NORMAL)
        self.rerun_btn.config(state=tk.DISABLED)
        self.open_result_btn.config(state=tk.DISABLED)
        self.pass_count.set(0)
        self.fail_count.set(0)
        self.review_count.set(0)
        self.ocr_count.set(0)
        self.progress_value.set(0)
        self.progress_percent_var.set("0%")
        self.stage_var.set("Starting")
        self.review_files = []
        self.review_listbox.delete(0, tk.END)
        
        # Clear log text
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.NORMAL)

    def update_ui_for_finish(self, status):
        self.is_processing = False
        self.status_current_file.set(f"Job {status}!")
        self.stage_var.set("Complete")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        self.stop_btn.config(state=tk.DISABLED)
        self.cancel_progress_btn.config(state=tk.DISABLED)
        self.rerun_btn.config(state=tk.NORMAL)
        self.is_paused = False
        self.pause_event.clear()
        self.update_review_list()
        
        # Calculate elapsed time
        if self.start_time:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
            self.log_message(f"Processing completed in {time_str}", "info")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_event.set()
            self.pause_btn.config(text="Resume")
            self.stage_var.set("Paused")
            self.log_message("Processing paused", "warning")
        else:
            self.pause_event.clear()
            self.pause_btn.config(text="Pause")
            self.stage_var.set("Processing")
            self.log_message("Processing resumed", "info")

    def stop_processing(self):
        if messagebox.askyesno("Stop Job", "Are you sure you want to stop the current job?"):
            self.cancel_event.set()
            self.log_message("Stopping processing...", "warning")
            self.stage_var.set("Stopping")

    def open_review_tool(self):
        try:
            if self.review_files:
                # If there are review files, use the first one
                ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", self.review_files[0])
            else:
                # Otherwise just open the pattern manager
                ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns")
        except Exception as e:
            self.log_message(f"Error opening review tool: {e}", "error")
            messagebox.showerror("Error", f"Could not open review tool:\n{e}")

    def open_result_file(self):
        if self.result_file_path and Path(self.result_file_path).exists():
            try:
                open_file(self.result_file_path)
                self.log_message(f"Opened result file: {Path(self.result_file_path).name}", "info")
            except Exception as e:
                self.log_message(f"Error opening result file: {e}", "error")
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showerror("File Not Found", "Result file not found or has been moved.")

    def update_review_list(self):
        review_dir = OUTPUT_DIR / "needs_review"
        if review_dir.exists():
            try:
                files = [f.name for f in review_dir.iterdir() if f.suffix == '.txt']
                self.review_listbox.delete(0, tk.END)
                for file in files:
                    self.review_listbox.insert(tk.END, file)
                self.log_message(f"Found {len(files)} files that need review", "info")
            except Exception as e:
                self.log_message(f"Error reading review files: {e}", "error")

    def get_review_files(self):
        review_dir = OUTPUT_DIR / "needs_review"
        if not review_dir.exists():
            return []
            
        try:
            return [f for f in review_dir.iterdir() if f.suffix == '.txt']
        except Exception as e:
            self.log_message(f"Error reading review files: {e}", "error")
            return []

    def review_selected_file(self):
        selected_indices = self.review_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Please select a file from the list to review.")
            return
        
        filename = self.review_listbox.get(selected_indices[0])
        file_path = OUTPUT_DIR / "needs_review" / filename
        
        if not file_path.exists():
            messagebox.showerror("File Not Found", f"The file {filename} was not found in the review folder.")
            self.update_review_list()  # Refresh the list
            return
        
        file_info = {"txt_path": file_path}
        try:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", file_info)
        except Exception as e:
            self.log_message(f"Error opening review for {filename}: {e}", "error")
            messagebox.showerror("Error", f"Could not open review tool:\n{e}")

    def toggle_fullscreen(self, event=None):
        state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not state)
        return "break"

    def log_message(self, message, level="info"):
        """Add a message to the log text widget with the appropriate tag."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.NORMAL)

def main():
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        # Try to log the error
        try:
            logger.error(f"Critical error in application: {e}\n{traceback.format_exc()}")
        except:
            pass
            
        # Show error message
        messagebox.showerror("Application Error", f"The application encountered a critical error and must close:\n\n{e}")
        
        # Try to write error to file
        try:
            with open("app_error.log", "w") as f:
                f.write(f"Error: {e}\n\n{traceback.format_exc()}")
        except:
            pass

if __name__ == "__main__":
    main()