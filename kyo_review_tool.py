# kyo_review_tool.py
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import re
import logging
from logging_config import configure_logging
import traceback

logger = configure_logging("review_tool")

try:
    from config import BRAND_COLORS, PDF_TXT_DIR
except ImportError:
    BRAND_COLORS = {"background": "#F0F2F5"}
    PDF_TXT_DIR = Path("PDF_TXT")

class ReviewWindow(tk.Toplevel):
    """A Toplevel window for reviewing files and managing patterns."""
    def __init__(self, parent, pattern_type, pattern_title, file_info):
        super().__init__(parent)
        self.parent = parent
        self.file_info = file_info
        
        self.title(f"Pattern Review: {file_info.get('filename', 'N/A')}")
        self.geometry("900x700")
        self.configure(bg=BRAND_COLORS.get("background"))

        self._create_widgets()
        self._load_file_text()

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top pane for text display
        text_frame = ttk.Frame(main_pane)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        self.pdf_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10), relief=tk.FLAT)
        self.pdf_text.grid(row=0, column=0, sticky="nsew")
        text_scroll = ttk.Scrollbar(text_frame, command=self.pdf_text.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        self.pdf_text.config(yscrollcommand=text_scroll.set)
        main_pane.add(text_frame, weight=3)

        # Bottom pane for controls
        controls_frame = ttk.Frame(main_pane, padding=10)
        # Add any review controls here if needed in the future
        main_pane.add(controls_frame, weight=1)

        self.status_var = tk.StringVar(value="Loading...")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_file_text(self):
        """Loads the content for the selected file into the text widget."""
        self.pdf_text.config(state=tk.NORMAL)
        self.pdf_text.delete("1.0", tk.END)

        try:
            if not self.file_info:
                raise ValueError("No file information provided.")

            # --- FIXED: Handle locked files gracefully ---
            if self.file_info.get("reason") == "File Locked":
                locked_msg = (
                    f"--- FILE LOCKED ---\n\n"
                    f"File: {self.file_info['filename']}\n\n"
                    "This file could not be processed because it is locked by another application.\n"
                    "Please close the file in other programs (like Adobe Acrobat) and run the tool again."
                )
                self.pdf_text.insert("1.0", locked_msg)
                self.status_var.set("Cannot review a locked file.")
                return

            txt_path_str = self.file_info.get("txt_path")
            if not txt_path_str:
                raise FileNotFoundError("No text path found in review data.")
            
            txt_path = Path(txt_path_str)
            if not txt_path.exists():
                raise FileNotFoundError(f"Review text file not found at: {txt_path}")

            with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            self.pdf_text.insert("1.0", content)
            self.status_var.set(f"Loaded for review: {txt_path.name}")

        except Exception as e:
            error_msg = f"Failed to load review file: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.pdf_text.insert("1.0", f"ERROR: {error_msg}")
        finally:
            self.pdf_text.config(state=tk.DISABLED)
