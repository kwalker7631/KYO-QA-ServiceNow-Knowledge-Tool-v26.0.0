# kyo_qa_tool_app.py
# Version: 30.0.0
# Last modified: 2025-07-06

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import queue
import time
import sys

from processing_engine import run_processing_job
from file_utils import ensure_folders, cleanup_directory, extract_zip_to_temp
from kyo_review_tool import ReviewWindow
from version import VERSION
import logging_utils
from gui_components import (
    setup_high_contrast_styles,
    create_main_header, 
    create_io_section,
    create_controls_section, 
    create_live_status_section,
)

logger = logging_utils.setup_logger("app")

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- State and Control Variables ---
        self.count_processed = tk.IntVar(value=0)
        self.count_pass = tk.IntVar(value=0)
        self.count_fail = tk.IntVar(value=0)
        self.count_review = tk.IntVar(value=0)
        
        self.is_processing = False
        self.result_file_path = None
        self.reviewable_files = []
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.spinner_running = False
        
        self.selected_folder = tk.StringVar()
        self.selected_excel = tk.StringVar()
        self.selected_files_list = []
        
        self.status_current_file = tk.StringVar(value="Ready to start.")
        self.progress_value = tk.DoubleVar(value=0)
        
        self.is_fullscreen = False
        self.temp_dir_to_clean = None

        # --- Initialize UI ---
        self._setup_window()
        self._create_widgets()
        
        ensure_folders()
        self.after(100, self.process_response_queue)

    def _setup_window(self):
        """Configures the main application window."""
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1100x850")
        self.minsize(950, 750)
        
        setup_high_contrast_styles(self)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Escape>", self.toggle_fullscreen)

    def _create_widgets(self):
        """Creates and lays out all the UI components."""
        create_main_header(self, VERSION)
        create_io_section(self, self)
        create_controls_section(self, self)
        create_live_status_section(self, self)

    def log_message(self, message, level="info"):
        """Adds a timestamped message to the log text widget."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_processing(self):
        """Validates inputs and starts the processing job in a thread."""
        if self.is_processing:
            return
        
        input_path = self.selected_folder.get() or self.selected_files_list
        if not input_path:
            messagebox.showwarning(
                "Input Missing",
                "Please select a PDF source (folder, files, or ZIP).",
            )
            return
        excel_path = self.selected_excel.get()
        if not excel_path:
            messagebox.showwarning(
                "Input Missing",
                "Please select an Excel template file.",
            )
            return
            
        job = {"excel_path": excel_path, "input_path": input_path}
        
        self.update_ui_for_start()
        self.log_message("Starting processing job...", "info")
        
        threading.Thread(
            target=run_processing_job,
            args=(job, self.response_queue, self.cancel_event, self.pause_event),
            daemon=True,
        ).start()

    def browse_zip(self):
        """Handles browsing for and extracting a ZIP archive."""
        path = filedialog.askopenfilename(title="Select ZIP Archive", filetypes=[("ZIP Archives", "*.zip")])
        if not path:
            return

        zip_path = Path(path)
        self.log_message(f"Extracting PDFs from: {zip_path.name}", "info")
        
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
        
        temp_dir = extract_zip_to_temp(zip_path)
        if not temp_dir:
            self.log_message("Failed to extract ZIP file.", "error")
            return
            
        self.temp_dir_to_clean = temp_dir
        pdf_files = list(temp_dir.glob('**/*.pdf'))
        
        if not pdf_files:
            self.log_message("No PDF files found in the ZIP archive.", "warning")
            cleanup_directory(self.temp_dir_to_clean)
            self.temp_dir_to_clean = None
            return
            
        self.selected_files_list = pdf_files
        self.selected_folder.set(f"[ZIP] {zip_path.name} ({len(pdf_files)} files)")
        self.log_message(f"Ready to process {len(pdf_files)} files from {zip_path.name}.", "success")

    def browse_excel(self):
        path = filedialog.askopenfilename(
            title="Select Excel Template", filetypes=[("Excel Files", "*.xlsx *.xlsm")]
        )
        if path:
            self.selected_excel.set(path)

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_folder.set(path)
            self.selected_files_list = []

    def browse_files(self):
        paths = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
        if paths:
            self.selected_files_list = list(paths)
            self.selected_folder.set(f"{len(paths)} files selected")

    def on_closing(self):
        """Handles the application closing event."""
        if self.is_processing and not messagebox.askyesno("Exit Confirmation", "A job is running. Are you sure?"):
            return
        
        self.cancel_event.set()
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
        
        self.destroy()

    def toggle_fullscreen(self, event=None):
        """Toggles the main window's fullscreen state."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def update_ui_for_start(self):
        """Disables UI and resets counters when processing starts."""
        self.is_processing = True
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        self.process_btn.config(state=tk.DISABLED)

        self.spinner_running = True
        threading.Thread(target=self._spinner_worker, daemon=True).start()
        
        # Reset counters
        for var in [self.count_processed, self.count_pass, self.count_fail, self.count_review]:
            var.set(0)
        self.progress_value.set(0)
        self.status_current_file.set("Initializing job...")

    def update_ui_for_finish(self, status):
        """Re-enables UI when processing finishes."""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.status_current_file.set(f"Job {status}.")
        self.spinner_running = False
        if hasattr(self, "spinner_label"):
            self.spinner_label.config(text="")
        
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
            self.temp_dir_to_clean = None

    def _spinner_worker(self):
        frames = "|/-\\"
        idx = 0
        while self.spinner_running and not self.cancel_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.2)
                continue
            if hasattr(self, "spinner_label"):
                self.spinner_label.config(text=frames[idx % len(frames)])
            idx += 1
            time.sleep(0.1)

    def open_review_for_selected_file(self):
        """Opens the pattern review tool for the selected file."""
        selection = self.review_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file from the list to review.")
            return
            
        item_id = selection[0]
        filename = self.review_tree.item(item_id, "values")[0]
        review_info = next((f for f in self.reviewable_files if f['filename'] == filename), None)
        
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
        else:
            messagebox.showerror("Error", "Could not find review data for the selected file.")

    def process_response_queue(self):
        """Processes messages from the processing thread to update the UI."""
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "log":
                    self.log_message(msg.get("msg", ""), msg.get("tag", "info"))
                elif msg_type == "status":
                    self.status_current_file.set(msg.get("msg", "..."))
                elif msg_type == "progress":
                    self.progress_value.set(msg.get("value", 0))
                elif msg_type == "update_counts":
                    self.count_processed.set(self.count_processed.get() + 1)
                    status = msg.get("status")
                    if status == "Pass":
                        self.count_pass.set(self.count_pass.get() + 1)
                    elif status == "Fail":
                        self.count_fail.set(self.count_fail.get() + 1)
                    elif status == "Needs Review":
                        self.count_review.set(self.count_review.get() + 1)
                elif msg_type == "review_item":
                    data = msg.get("data", {})
                    if data:
                        self.reviewable_files.append(data)
                        self.review_tree.insert('', 'end', values=(data.get('filename'),))
                elif msg_type == "finish":
                    self.update_ui_for_finish(msg.get("status", "Complete"))

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_response_queue)
            
    # --- Placeholder/Simple Implementations for other controls ---
    def stop_processing(self):
        if messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the current job?"):
            self.cancel_event.set()
            self.log_message("Stop request sent to processing thread.", "warning")

    def pause_processing(self):
        self.pause_event.set()
        self.status_current_file.set("Processing paused")
        self.log_message("Processing paused", "info")

    def resume_processing(self):
        self.pause_event.clear()
        self.status_current_file.set("Resuming...")
        self.log_message("Processing resumed", "info")

def main():
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        logger.error("Application failed to start.", exc_info=True)
        messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close:\n\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
