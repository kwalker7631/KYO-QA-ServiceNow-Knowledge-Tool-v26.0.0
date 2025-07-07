# kyo_qa_tool_app.py
# Version: 33.0.0
# Last modified: 2025-07-06

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import queue
import time
import sys
import os

from processing_engine import process_job
from file_utils import (
    ensure_folders,
    cleanup_directory,
    extract_zip_to_temp,
    open_file_in_default_app,
)
from kyo_review_tool import ReviewWindow
from version import VERSION
import logging_utils
from gui_components import (
    setup_high_contrast_styles,
    create_main_header,
    create_io_section,
    create_controls_section,
    create_live_status_section,
    create_footer,
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
        self.count_ocr = tk.IntVar(value=0)

        self.is_processing = False
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
        self.progress_percent_var = tk.StringVar(value="0%")

        self.is_fullscreen = False
        self.fullscreen_status_var = tk.StringVar(value="")
        self.temp_dir_to_clean = None

        # --- Initialize UI ---
        self._setup_window()
        self._create_widgets()

        ensure_folders()
        self.after(100, self.process_response_queue)

    def _setup_window(self):
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1200x900")
        self.minsize(1000, 800)
        setup_high_contrast_styles(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        create_main_header(main_frame, VERSION)
        create_io_section(main_frame, self)
        create_controls_section(main_frame, self)
        create_live_status_section(main_frame, self)
        create_footer(self, self)

    def log_message(self, message, level="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_processing(self):
        if self.is_processing:
            return

        if self.selected_files_list:
            input_path = self.selected_files_list
        else:
            folder_path_str = self.selected_folder.get().split(" (")[0]
            input_path = Path(folder_path_str) if folder_path_str else ""

        if not input_path:
            messagebox.showwarning("Input Missing", "Please select a PDF source.")
            return
        excel_path = self.selected_excel.get()
        if not excel_path:
            messagebox.showwarning(
                "Input Missing", "Please select an Excel template file."
            )
            return

        job = {"excel_path": excel_path, "input_path": input_path}
        self.update_ui_for_start()
        threading.Thread(
            target=process_job,
            args=(
                job,
                {
                    "progress_queue": self.response_queue,
                    "cancel_event": self.cancel_event,
                    "pause_event": self.pause_event,
                },
            ),
            daemon=True,
        ).start()

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_files_list.clear()
            try:
                pdf_files = list(Path(path).glob("**/*.pdf"))
                self.selected_folder.set(f"{path} ({len(pdf_files)} PDF file(s) found)")
                self.log_message(
                    f"{len(pdf_files)} PDF(s) found in selected folder.", "info"
                )
            except Exception as e:
                self.log_message(f"Error counting files: {e}", "error")
                self.selected_folder.set(path)

    def browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")]
        )
        if paths:
            self.selected_files_list = [Path(p) for p in paths]
            self.selected_folder.set(f"{len(paths)} files selected")

    def browse_zip(self):
        path = filedialog.askopenfilename(
            title="Select ZIP Archive", filetypes=[("ZIP Archives", "*.zip")]
        )
        if not path:
            return
        zip_path = Path(path)
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
        temp_dir = extract_zip_to_temp(zip_path)
        if not temp_dir:
            self.log_message("Failed to extract ZIP file.", "error")
            return
        self.temp_dir_to_clean = temp_dir
        pdf_files = list(temp_dir.glob("**/*.pdf"))
        self.selected_files_list = pdf_files
        self.selected_folder.set(f"[ZIP] {zip_path.name} ({len(pdf_files)} files)")

    def browse_excel(self):
        path = filedialog.askopenfilename(
            title="Select Excel Template", filetypes=[("Excel Files", "*.xlsx *.xlsm")]
        )
        if path:
            self.selected_excel.set(path)

    def on_closing(self):
        if self.is_processing and not messagebox.askyesno(
            "Exit Confirmation", "A job is running. Are you sure you want to exit?"
        ):
            return
        self.cancel_event.set()
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
        self.destroy()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        self.fullscreen_status_var.set(
            "Fullscreen (Press F11 or Esc to exit)" if self.is_fullscreen else ""
        )

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()

    def update_ui_for_start(self):
        self.is_processing = True
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        self.process_btn.config(state=tk.DISABLED)
        self.spinner_running = True
        threading.Thread(target=self._spinner_worker, daemon=True).start()
        if hasattr(self, "footer_spinner"):
            self.footer_spinner.config(text="|")
        for var in [
            self.count_processed,
            self.count_pass,
            self.count_fail,
            self.count_review,
            self.count_ocr,
        ]:
            var.set(0)
        self.progress_value.set(0)
        self.progress_percent_var.set("0%")
        self.status_current_file.set("Initializing job...")

    def update_ui_for_finish(self, status, data=None):
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.status_current_file.set(f"Job {status}.")
        self.spinner_running = False
        if hasattr(self, "spinner_label"):
            self.spinner_label.config(text="")
        if hasattr(self, "footer_spinner"):
            self.footer_spinner.config(text="")
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
            self.temp_dir_to_clean = None

        if status == "Complete" and data and data.get("output_path"):
            if messagebox.askyesno(
                "Processing Complete",
                f"Results saved to:\n{data['output_path']}\n\nDo you want to open the file now?",
            ):
                open_file_in_default_app(data["output_path"])

    def _spinner_worker(self):
        frames = "|/-\\"
        idx = 0
        while self.spinner_running and not self.cancel_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.2)
                continue
            if hasattr(self, "spinner_label"):
                self.spinner_label.config(text=frames[idx % len(frames)])
            if hasattr(self, "footer_spinner"):
                self.footer_spinner.config(text=frames[idx % len(frames)])
            idx += 1
            time.sleep(0.1)

    def open_review_for_selected_file(self):
        selection = self.review_tree.selection()
        if not selection:
            return
        item_id = selection[0]
        filename = self.review_tree.item(item_id, "values")[0]
        review_info = next(
            (f for f in self.reviewable_files if f["filename"] == filename), None
        )
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)

    def process_response_queue(self):
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "log":
                    self.log_message(msg.get("msg", ""), msg.get("tag", "info"))
                elif msg_type == "status":
                    self.status_current_file.set(msg.get("msg", "..."))
                elif msg_type == "progress":
                    val = msg.get("value", 0)
                    self.progress_value.set(val)
                    self.progress_percent_var.set(f"{int(val)}%")
                elif msg_type == "update_counts":
                    self.count_processed.set(self.count_processed.get() + 1)
                    status = msg.get("status")
                    if status == "Pass":
                        self.count_pass.set(self.count_pass.get() + 1)
                    elif status == "Fail":
                        self.count_fail.set(self.count_fail.get() + 1)
                    elif status == "Needs Review":
                        self.count_review.set(self.count_review.get() + 1)
                elif msg_type == "increment_ocr_counter":
                    self.count_ocr.set(self.count_ocr.get() + 1)
                elif msg_type == "review_item":
                    data = msg.get("data", {})
                    if data:
                        self.reviewable_files.append(data)
                        self.review_tree.insert(
                            "", "end", values=(data.get("filename"),)
                        )
                elif msg_type == "finish":
                    self.update_ui_for_finish(
                        msg.get("status", "Complete"), msg.get("data")
                    )
                    data = msg.get("data", {})
                    if data and data.get("output_path"):
                        self.status_current_file.set(
                            f"Export complete: {Path(data['output_path']).name}"
                        )
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_response_queue)


def main():
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        logger.error("Application failed to start.", exc_info=True)
        messagebox.showerror(
            "Fatal Error",
            f"A critical error occurred and the application must close:\n\n{e}",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
