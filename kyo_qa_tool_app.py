# kyo_qa_tool_app.py
# Version: 33.1.2
# Last modified: 2025-07-13

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import queue
import time
import sys
import json
import logging

from ocr_utils import extract_text_from_pdf
from data_harvesters import harvest_all_data
from excel_generator import ExcelGenerator
from file_utils import (
    ensure_folders,
    cleanup_directory,
    extract_zip_to_temp,
    open_file_in_default_app,
)
from kyo_review_tool import ReviewWindow
from version import VERSION
from config import CACHE_DIR, OUTPUT_DIR
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
import processing_engine as pe
from app_state import AppState


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


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
        self.reviewable_files = [] # For the main process tab
        self.loaded_cache_data = [] # For the review tab
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.spinner_running = False

        self.selected_folder = tk.StringVar()
        self.selected_excel = tk.StringVar()
        self.selected_files_list = []
        self.review_filter = tk.StringVar(value="All")
        self.harvest_file = tk.StringVar()

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
        excel_path_str = self.selected_excel.get()
        if not excel_path_str:
            messagebox.showwarning(
                "Input Missing", "Please select an Excel template file."
            )
            return
        excel_path = Path(excel_path_str)

        job = {"excel_path": excel_path, "input_path": input_path}
        self.update_ui_for_start()
        
        app_state = AppState(
            progress_queue=self.response_queue,
            cancel_event=self.cancel_event,
            pause_event=self.pause_event,
        )

        threading.Thread(
            target=self.run_processing_job,
            args=(job, app_state),
            daemon=True,
        ).start()

    def run_processing_job(self, job, app_state):
        try:
            raw_data = pe.fetch_data(job, app_state)
            if app_state.is_cancelled():
                app_state.finish_run("Cancelled")
                return

            passed_items, review_items = pe.parse_data(raw_data, app_state)
            
            if app_state.is_cancelled():
                app_state.finish_run("Cancelled")
                return
            
            all_results = passed_items + review_items
            output_path, skipped = pe.export_to_excel(all_results, job["excel_path"], app_state)
            
            app_state.finish_run("Complete", str(output_path))

        except Exception as e:
            logger.error(f"Processing job failed: {e}", exc_info=True)
            app_state.log(f"Critical error in processing thread: {e}", "error")
            app_state.finish_run("Failed")

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_files_list.clear()
            try:
                pdf_files = list(Path(path).glob("**/*.pdf"))
                self.selected_folder.set(f"{path} ({len(pdf_files)} PDF file(s) found)")
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
        if not path: return
        zip_path = Path(path)
        if self.temp_dir_to_clean:
            cleanup_directory(self.temp_dir_to_clean)
        temp_dir = extract_zip_to_temp(zip_path)
        if not temp_dir:
            self.log_message("Failed to extract ZIP file.", "error")
            return
        self.temp_dir_to_clean = temp_dir
        self.selected_files_list = list(temp_dir.glob("**/*.pdf"))
        self.selected_folder.set(f"[ZIP] {zip_path.name} ({len(self.selected_files_list)} files)")

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
        if not self.pause_event.is_set():
            self.pause_event.set()
            self.status_current_file.set("Processing paused")
            self.log_message("Processing paused by user.", "warning")

    def resume_processing(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.status_current_file.set("Resuming...")
            self.log_message("Processing resumed by user.", "info")

    def update_ui_for_start(self):
        self.is_processing = True
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        self.process_btn.config(state=tk.DISABLED)
        self.cancel_event.clear()
        self.pause_event.clear()
        self.spinner_running = True
        threading.Thread(target=self._spinner_worker, daemon=True).start()
        for var in [self.count_processed, self.count_pass, self.count_fail, self.count_review, self.count_ocr]:
            var.set(0)
        self.progress_value.set(0)
        self.progress_percent_var.set("0%")
        self.status_current_file.set("Initializing job...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Starting new processing job...", "info")

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
            output_path = data['output_path']
            self.log_message(f"Processing complete. Report saved to {output_path}", "info")
            if messagebox.askyesno(
                "Processing Complete",
                f"Results saved to:\n{output_path}\n\nDo you want to open the file now?",
            ):
                open_file_in_default_app(output_path)
        else:
            self.log_message(f"Job finished with status: {status}", "warning" if status != "Cancelled" else "info")

    def _spinner_worker(self):
        frames = "|/-\\"
        idx = 0
        while self.spinner_running:
            if self.pause_event.is_set():
                time.sleep(0.2)
                continue
            if hasattr(self, "spinner_label"):
                self.spinner_label.config(text=frames[idx % len(frames)])
            idx += 1
            time.sleep(0.1)

    def harvest_single_file(self):
        path_str = self.harvest_file.get()
        if not path_str:
            messagebox.showwarning("Input Missing", "Please select a PDF file to harvest.")
            return
        pdf = Path(path_str)
        if not pdf.exists():
            messagebox.showerror("File Not Found", f"{pdf} does not exist")
            return
        
        self.harvest_text.config(state=tk.NORMAL)
        self.harvest_text.delete("1.0", tk.END)
        self.harvest_text.insert("1.0", "Harvesting...")
        self.harvest_text.config(state=tk.DISABLED)
        self.harvest_export_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._harvest_worker, args=(pdf,), daemon=True).start()

    def _harvest_worker(self, pdf):
        try:
            text, _ = extract_text_from_pdf(str(pdf.resolve()), use_ocr=True)
            data = harvest_all_data(text, pdf.name)
            self.harvest_results = [data]
            meta_display = "; ".join([f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in data.get('meta', {}).items()])
            result_text = (
                f"Filename: {data.get('filename', 'N/A')}\n"
                f"QA Number: {data.get('qa_number', 'N/A')}\n"
                f"Author: {data.get('author', 'N/A')}\n"
                f"Meta: {meta_display}"
            )
            self.response_queue.put({"type": "harvest_result", "text": result_text})
        except Exception as e:
            error_message = f"Harvest failed for {pdf.name}: {e}"
            logger.error(error_message, exc_info=True)
            self.response_queue.put({"type": "harvest_error", "text": error_message})

    def export_harvest_results(self):
        if not getattr(self, "harvest_results", None):
            messagebox.showinfo("No Data", "Nothing to export.")
            return
        
        excel_template_str = self.selected_excel.get()
        if not excel_template_str:
            messagebox.showwarning("Template Missing", "Please select an Excel template file first on the 'Process' tab.")
            return
        excel_template = Path(excel_template_str)

        try:
            pdf = Path(self.harvest_file.get())
            output_filename = OUTPUT_DIR / f"{pdf.stem}_harvested.xlsx"
            generator = ExcelGenerator(str(excel_template))
            output_path, skipped_files = generator.create_report(self.harvest_results, str(output_filename))
            if skipped_files:
                 self.log_message(f"Export of single harvest complete, but skipped file: {skipped_files[0]}", "warning")
            else:
                 self.log_message(f"Single harvest exported successfully to {output_path}", "info")
            if messagebox.askyesno("Export Complete", f"Harvested data exported to:\n{output_path}\n\nOpen it now?"):
                open_file_in_default_app(str(output_path))
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            self.log_message(f"Export failed: {e}", "error")

    def manual_export(self):
        excel_path_str = self.selected_excel.get()
        if not excel_path_str:
            messagebox.showwarning("Input Missing", "Please select an Excel template file.")
            return
        excel_path = Path(excel_path_str)
        cache_files = list(CACHE_DIR.glob("*.json"))
        if not cache_files:
            messagebox.showinfo("No Data", "No cached results found to export.")
            return
        results = []
        for jf in cache_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    results.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed loading cached file {jf}: {e}")
        if not results:
            messagebox.showinfo("No Data", "Could not load any valid data from cache.")
            return
        try:
            app_state = AppState(
                progress_queue=self.response_queue,
                cancel_event=threading.Event(),
                pause_event=threading.Event(),
            )
            output_path, skipped = pe.export_to_excel(results, excel_path, app_state)
            if output_path:
                msg = f"Cached results exported to:\n{output_path}"
                if skipped:
                    msg += f"\n\nSkipped files: {', '.join(skipped)}"
                if messagebox.askyesno("Export Complete", f"{msg}\n\nDo you want to open the file now?"):
                    open_file_in_default_app(str(output_path))
            else:
                messagebox.showerror("Export Failed", "Failed to create the Excel file from cache.")
        except Exception as e:
            logger.error(f"Manual export failed: {e}", exc_info=True)
            messagebox.showerror("Export Error", f"An error occurred during manual export: {e}")

    def open_review_for_selected_file(self):
        selection = self.review_tree.selection()
        if not selection: return
        item_id = selection[0]
        filename = self.review_tree.item(item_id, "values")[0]
        review_info = next((f for f in self.reviewable_files if f.get("filename") == filename), None)
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
        else:
            messagebox.showerror("Error", f"Could not find review data for {filename}")

    def open_review_from_review_tab(self):
        selection = self.review_table.selection()
        if not selection: return
        item_id = selection[0]
        filename = self.review_table.item(item_id, "values")[0]
        review_info = next((f for f in self.loaded_cache_data if f.get("filename") == filename), None)
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
        else:
            messagebox.showerror("Error", f"Could not find cached review data for {filename}. Try loading again.")

    def load_review_data(self):
        filter_status = self.review_filter.get()
        self.review_table.delete(*self.review_table.get_children())
        self.loaded_cache_data.clear()

        cache_files = list(CACHE_DIR.glob("*.json"))
        if not cache_files:
            self.empty_label.grid(row=0, column=0, sticky="nsew")
            return
        
        self.empty_label.grid_forget()

        for json_file in cache_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.loaded_cache_data.append(data)
            except Exception as e:
                logger.error(f"Failed loading review data from {json_file}: {e}")
                continue
            
            status = data.get("status", "Unknown")
            if filter_status != "All" and status != filter_status:
                continue

            filename = data.get("filename", "Unknown File")
            review_reason = data.get("review_reason", "")
            
            iid = self.review_table.insert("", "end", values=(filename, status, review_reason))
            if status == "Needs Review":
                self.review_table.item(iid, tags=("review",))
            elif status == "Fail":
                self.review_table.item(iid, tags=("fail",))

        if not self.review_table.get_children():
            self.empty_label.grid(row=0, column=0, sticky="nsew")


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
                    if status == "Pass": self.count_pass.set(self.count_pass.get() + 1)
                    elif status == "Fail": self.count_fail.set(self.count_fail.get() + 1)
                    elif status == "Needs Review": self.count_review.set(self.count_review.get() + 1)
                elif msg_type == "increment_ocr_counter":
                    self.count_ocr.set(self.count_ocr.get() + 1)
                elif msg_type == "review_item":
                    data = msg.get("data", {})
                    if data:
                        self.reviewable_files.append(data)
                        self.review_tree.insert("", "end", values=(data.get("filename"), data.get("review_reason", "")))
                elif msg_type == "finish":
                    self.update_ui_for_finish(msg.get("status", "Complete"), msg.get("data"))
                elif msg_type == "harvest_result":
                    self.harvest_text.config(state=tk.NORMAL)
                    self.harvest_text.delete("1.0", tk.END)
                    self.harvest_text.insert("1.0", msg.get("text", ""))
                    self.harvest_text.config(state=tk.DISABLED)
                    self.harvest_export_btn.config(state=tk.NORMAL)
                elif msg_type == "harvest_error":
                    self.harvest_text.config(state=tk.NORMAL)
                    self.harvest_text.delete("1.0", tk.END)
                    self.harvest_text.insert("1.0", msg.get("text", "An unknown error occurred."))
                    self.harvest_text.config(state=tk.DISABLED)
                    self.harvest_export_btn.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_response_queue)


def main():
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        logger.critical("Application failed to start.", exc_info=True)
        messagebox.showerror(
            "Fatal Error",
            f"A critical error occurred and the application must close:\n\n{e}",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
