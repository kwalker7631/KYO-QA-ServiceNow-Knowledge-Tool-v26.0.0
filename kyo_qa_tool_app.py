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
import json

from processing_engine import process_job
from ocr_utils import extract_text_from_pdf
from data_harvesters import harvest_all_data
from utils import ExcelGenerator
from file_utils import (
    ensure_folders,
    cleanup_directory,
    extract_zip_to_temp,
    open_file_in_default_app,
)
from kyo_review_tool import ReviewWindow
from version import VERSION
import logging_utils
from config import CACHE_DIR
from gui_components import (
    setup_high_contrast_styles,
    create_main_header,
    create_io_section,
    create_controls_section,
    create_live_status_section,
    create_footer,
    create_review_tab,
    create_harvest_tab,
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
        self.review_filter = tk.StringVar(value="All")

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
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        process_tab = ttk.Frame(self.notebook)
        review_tab = ttk.Frame(self.notebook)
        harvest_tab = ttk.Frame(self.notebook)
        self.notebook.add(process_tab, text="Process")
        self.notebook.add(review_tab, text="Review")
        self.notebook.add(harvest_tab, text="Harvest")

        create_main_header(process_tab, VERSION)
        create_io_section(process_tab, self)
        create_controls_section(process_tab, self)
        create_live_status_section(process_tab, self)

        create_review_tab(review_tab, self)
        create_harvest_tab(harvest_tab, self)

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

        import processing_engine as pe

        job = {"excel_path": excel_path, "input_path": input_path}
        self.update_ui_for_start()
        threading.Thread(
            target=pe.process_job,
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

    def browse_harvest_file(self):
        path = filedialog.askopenfilename(
            title="Select PDF File", filetypes=[("PDF Files", "*.pdf")]
        )
        if path:
            self.harvest_file.set(path)

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

    def pause_processing(self):
        """Pause the current job."""
        if not self.pause_event.is_set():
            self.pause_event.set()
            if hasattr(self, "status_current_file"):
                self.status_current_file.set("Processing paused")

    def resume_processing(self):
        """Resume a paused job."""
        if self.pause_event.is_set():
            self.pause_event.clear()
            if hasattr(self, "status_current_file"):
                self.status_current_file.set("Resuming...")

    def update_ui_for_start(self):
        self.is_processing = True
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        self.process_btn.config(state=tk.DISABLED)
        self.spinner_running = True
        threading.Thread(target=self._spinner_worker, daemon=True).start()
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
        cancel_evt = self.__dict__.get("cancel_event", threading.Event())
        pause_evt = self.__dict__.get("pause_event", threading.Event())
        while self.spinner_running and not cancel_evt.is_set():
            if pause_evt.is_set():
                time.sleep(0.2)
                continue
            if hasattr(self, "spinner_label"):
                self.spinner_label.config(text=frames[idx % len(frames)])
            idx += 1
            time.sleep(0.1)

    def harvest_single_file(self):
        path_str = self.harvest_file.get()
        if not path_str:
            messagebox.showwarning(
                "Input Missing", "Please select a PDF file to harvest."
            )
            return
        pdf = Path(path_str)
        if not pdf.exists():
            messagebox.showerror("File Not Found", f"{pdf} does not exist")
            return
        self.spinner_running = True
        threading.Thread(target=self._spinner_worker, daemon=True).start()
        threading.Thread(target=self._harvest_worker, args=(pdf,), daemon=True).start()

    def _harvest_worker(self, pdf):
        try:
            self.status_current_file.set(f"Harvesting {pdf.name}...")
            text = extract_text_from_pdf(str(pdf.resolve()))
            data = harvest_all_data(text, pdf.name)
            self.harvest_results = [{"filename": pdf.name, **data}]
            result_text = f"Models: {data.get('models')}\nAuthor: {data.get('author')}"
            self.harvest_text.config(state=tk.NORMAL)
            self.harvest_text.delete("1.0", tk.END)
            self.harvest_text.insert("1.0", result_text)
            self.harvest_text.config(state=tk.DISABLED)
            self.harvest_export_btn.config(state=tk.NORMAL)
            self.status_current_file.set("Harvest complete")
        except Exception as e:
            self.status_current_file.set(f"Harvest failed: {e}")
            messagebox.showerror("Harvest Error", str(e))
            self.harvest_results = []
            self.harvest_export_btn.config(state=tk.DISABLED)
        finally:
            self.spinner_running = False

    def export_harvest_results(self):
        if not getattr(self, "harvest_results", None):
            messagebox.showinfo("No Data", "Nothing to export.")
            return
        try:
            pdf = Path(self.harvest_file.get())
            out_path = pdf.with_name(pdf.stem + "_harvest.xlsx")
            ExcelGenerator(str(out_path)).create_report(self.harvest_results)
            self.status_current_file.set(f"Export complete: {out_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            self.status_current_file.set(f"Export failed: {e}")
            self.harvest_export_btn.config(state=tk.DISABLED)

    def manual_export(self):
        """Export cached JSON results to an Excel file."""
        excel_path = self.selected_excel.get()
        if not excel_path:
            messagebox.showwarning(
                "Input Missing", "Please select an Excel template file."
            )
            return

        cache_files = list(CACHE_DIR.glob("*.json"))
        if not cache_files:
            messagebox.showinfo("No Data", "No cached results found.")
            return

        results = []
        for jf in cache_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    results.append(json.load(f))
            except Exception as e:  # pragma: no cover - just log
                logger.error(f"Failed loading {jf}: {e}")

        try:
            import processing_engine as pe

            output, skipped = pe.export_to_excel(
                results, Path(excel_path), self.response_queue
            )
            if output:
                msg = f"Results exported to:\n{output}"
                if skipped:
                    msg += f"\nSkipped: {', '.join(skipped)}"
                messagebox.showinfo("Export Complete", msg)
            else:
                messagebox.showerror("Export Failed", "Failed to export to Excel.")
        except Exception as e:  # pragma: no cover - just log
            logger.error(f"Manual export failed: {e}", exc_info=True)
            messagebox.showerror("Export Error", str(e))

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

    def load_review_data(self):
        filter_status = (
            self.review_filter.get() if hasattr(self, "review_filter") else "All"
        )
        if hasattr(self, "review_table"):
            self.review_table.delete(*self.review_table.get_children())
        loaded = 0
        for json_file in CACHE_DIR.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Failed loading {json_file}: {e}")
                continue
            status = data.get("status", "Unknown")
            if filter_status != "All" and status != filter_status:
                continue
            if hasattr(self, "review_table"):
                iid = self.review_table.insert(
                    "", "end", values=(data.get("filename"), status)
                )
                loaded += 1
                if status == "Needs Review":
                    self.review_table.item(iid, tags=("review",))
                elif status == "Fail":
                    self.review_table.item(iid, tags=("fail",))
        if loaded == 0:
            messagebox.showinfo("Review", "No items found for the selected filter.")

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
