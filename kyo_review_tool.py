# kyo_review_tool.py
# Version: 1.1.0
# Last modified: 2025-07-13

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging
import json

from branding import KyoceraColors
from custom_patterns import PATTERNS_DIR

logger = logging.getLogger(__name__)

class ReviewWindow(tk.Toplevel):
    """A window for reviewing a file and editing associated regex patterns."""

    def __init__(self, parent, pattern_key, pattern_name, review_info):
        super().__init__(parent)
        self.pattern_key = pattern_key
        self.pattern_name = pattern_name
        self.review_info = review_info
        self.pattern_file_path = PATTERNS_DIR / f"{pattern_key.lower()}.json"

        self._setup_window()
        self._create_widgets()
        self._load_patterns()
        self._load_file_text()

    def _setup_window(self):
        self.title(f"Review File: {self.review_info.get('filename', 'Unknown')}")
        self.geometry("1200x800")
        self.configure(bg=KyoceraColors.BACKGROUND_MAIN)

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side: Text viewer
        text_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(text_frame, weight=2)
        
        ttk.Label(text_frame, text="File Content", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.text_widget = tk.Text(text_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10))
        text_scroll = ttk.Scrollbar(text_frame, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=text_scroll.set)
        text_scroll.pack(side="right", fill="y")
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Right side: Pattern editor
        pattern_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(pattern_frame, weight=1)

        ttk.Label(pattern_frame, text=f"Edit '{self.pattern_name}' Patterns", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.pattern_text = tk.Text(pattern_frame, wrap=tk.WORD, font=("Consolas", 10), height=15)
        pattern_scroll = ttk.Scrollbar(pattern_frame, command=self.pattern_text.yview)
        self.pattern_text.config(yscrollcommand=pattern_scroll.set)
        pattern_scroll.pack(side="right", fill="y")
        self.pattern_text.pack(side="left", fill="both", expand=True)
        
        save_btn = ttk.Button(pattern_frame, text="Save Patterns", command=self._save_patterns)
        save_btn.pack(pady=(10, 0), fill="x")

    def _load_file_text(self):
        """Loads the text from the cached file."""
        try:
            # Correctly look for the 'text_path' key
            text_file_path_str = self.review_info.get("text_path")
            if not text_file_path_str:
                raise FileNotFoundError("No text path found in review data.")
            
            text_file_path = Path(text_file_path_str)
            if not text_file_path.exists():
                raise FileNotFoundError(f"Cached text file does not exist: {text_file_path}")

            with open(text_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", content)
            self.text_widget.config(state=tk.DISABLED)

        except Exception as e:
            logger.error(f"Failed to load review file: {e}", exc_info=True)
            messagebox.showerror("Load Error", f"Could not load the text for review.\n\nReason: {e}", parent=self)
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", f"Error loading file: {e}")
            self.text_widget.config(state=tk.DISABLED)

    def _load_patterns(self):
        """Loads the current patterns from the JSON file."""
        try:
            if self.pattern_file_path.exists():
                with open(self.pattern_file_path, "r", encoding="utf-8") as f:
                    patterns = json.load(f)
                self.pattern_text.insert("1.0", "\n".join(patterns))
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load pattern file: {e}", parent=self)

    def _save_patterns(self):
        """Saves the edited patterns back to the JSON file."""
        try:
            patterns = self.pattern_text.get("1.0", tk.END).strip().split("\n")
            patterns = [p.strip() for p in patterns if p.strip()]  # Remove empty lines
            with open(self.pattern_file_path, "w", encoding="utf-8") as f:
                json.dump(patterns, f, indent=4)
            messagebox.showinfo("Success", f"Patterns for '{self.pattern_name}' saved successfully.", parent=self)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save pattern file: {e}", parent=self)
