# kyo_review_tool.py
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import re
import importlib
import logging
from logging_config import configure_logging
import traceback

# Configure logging
logger = configure_logging("review_tool")

# Try to import from config, with fallback
try:
    from config import BRAND_COLORS, PDF_TXT_DIR
except ImportError:
    # Fallback values
    BRAND_COLORS = {
        "background": "#F0F2F5",
        "highlight": "#0078D4",
        "success": "#107C10",
        "warning": "#FFA500",
        "error": "#DA291C",
    }
    PDF_TXT_DIR = Path("PDF_TXT")

def generate_regex_from_sample(sample: str) -> str:
    """
    Analyzes a sample string and generates a regex pattern, generalizing only the numbers.
    """
    if not sample or not sample.strip():
        return ""

    # Step 1: Escape any special regex characters in the user's sample text
    escaped_sample = re.escape(sample.strip())

    # Step 2: In the escaped string, find all digit sequences and replace them
    # with the regex token for one or more digits, `\d+`
    pattern_with_digit_wildcard = re.sub(r'\d+', r'\\d+', escaped_sample)
    
    # Step 3: Construct the final pattern with word boundaries
    return f"\\b{pattern_with_digit_wildcard}\\b"


class ReviewWindow(tk.Toplevel):
    """A regex pattern management tool that safely edits custom_patterns.py."""
    def __init__(self, parent, pattern_name: str, pattern_label: str, file_info: dict = None):
        super().__init__(parent)
        
        self.pattern_name = pattern_name
        self.pattern_label = pattern_label
        self.file_info = file_info
        self.custom_patterns_path = Path("custom_patterns.py")
        
        self.title(f"Manage Custom: {self.pattern_label}")
        self.geometry("1000x700")
        self.configure(bg="#F0F2F5")
        
        # Add status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Main content
        paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel - pattern manager
        manager_frame = ttk.Frame(paned_window, padding=10)
        manager_frame.columnconfigure(0, weight=1)
        manager_frame.rowconfigure(1, weight=1)
        paned_window.add(manager_frame, width=400)

        # Right panel - text viewer
        text_frame = ttk.Frame(paned_window, padding=10)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        paned_window.add(text_frame)
        
        # Pattern manager header
        ttk.Label(manager_frame, text=self.pattern_label, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        
        # Pattern listbox
        self.pattern_listbox = tk.Listbox(manager_frame, font=("Consolas", 9), height=15)
        self.pattern_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_pattern_select)
        pattern_scrollbar = ttk.Scrollbar(manager_frame, orient="vertical", command=self.pattern_listbox.yview)
        pattern_scrollbar.grid(row=1, column=2, sticky="ns", pady=5)
        self.pattern_listbox.config(yscrollcommand=pattern_scrollbar.set)
        
        # Button frame
        btn_frame = ttk.Frame(manager_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Add as New", command=self.add_pattern).pack(side="left", padx=5)
        self.remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_pattern, state=tk.DISABLED)
        self.remove_btn.pack(side="left", padx=5)
        
        # Pattern entry
        ttk.Label(manager_frame, text="Test / Edit Pattern:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10,0))
        self.pattern_entry = ttk.Entry(manager_frame, font=("Consolas", 10))
        self.pattern_entry.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        # Test buttons frame
        test_save_frame = ttk.Frame(manager_frame)
        test_save_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.suggest_btn = ttk.Button(test_save_frame, text="Suggest from Highlight", command=self.on_suggest_pattern)
        self.suggest_btn.pack(side="left", padx=5)
        self.test_btn = ttk.Button(test_save_frame, text="Test Pattern", command=self.test_pattern)
        self.test_btn.pack(side="left", padx=5)
        ttk.Button(test_save_frame, text="Update List", command=self.update_pattern_in_list).pack(side="left", padx=5)
        
        # Add Browse button to select review files
        files_frame = ttk.LabelFrame(manager_frame, text="Review Files", padding=(5, 5))
        files_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.files_listbox = tk.Listbox(files_frame, font=("Consolas", 9), height=5)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.files_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)
        
        refresh_btn = ttk.Button(files_frame, text="Refresh Files", command=self.load_review_files)
        refresh_btn.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Save button
        ttk.Button(manager_frame, text="Save All Patterns", command=self.save_patterns_to_config).grid(row=7, column=0, columnspan=2, pady=10, sticky="ew")

        # Text viewer
        self.pdf_text = tk.Text(text_frame, wrap="word", font=("Consolas", 9), relief="solid", borderwidth=1)
        self.pdf_text.pack(fill="both", expand=True, side="left")
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.pdf_text.yview)
        text_scrollbar.pack(fill="y", side="right")
        self.pdf_text.config(yscrollcommand=text_scrollbar.set)
        self.pdf_text.tag_configure("highlight", background="yellow", foreground="black")

        # Initialize
        self.load_patterns_from_config()
        self.load_review_files()
        
        if self.file_info:
            self.load_text_file()
        else:
            self.suggest_btn.config(state=tk.DISABLED)
            self.test_btn.config(state=tk.DISABLED)
            self.pdf_text.insert("1.0", "No file selected.\n\nManage patterns on the left without testing, or select a file from the 'Review Files' list.")
            self.pdf_text.config(state=tk.DISABLED)

    def load_review_files(self):
        """Load list of review files from the review directory."""
        self.files_listbox.delete(0, tk.END)
        
        try:
            if not PDF_TXT_DIR.exists():
                PDF_TXT_DIR.mkdir(parents=True, exist_ok=True)
                
            reviews_dir = PDF_TXT_DIR / "needs_review"
            if not reviews_dir.exists():
                reviews_dir.mkdir(parents=True, exist_ok=True)
                
            # Get all .txt files in the directory
            review_files = []
            for path in reviews_dir.glob("*.txt"):
                review_files.append(path.name)
            
            for filename in sorted(review_files):
                self.files_listbox.insert(tk.END, filename)
                
            self.status_var.set(f"Found {len(review_files)} review files")
        except Exception as e:
            self.status_var.set(f"Error loading review files: {e}")
            logger.error(f"Error loading review files: {e}")

    def on_file_select(self, event):
        """Handle selection of a file from the list."""
        try:
            selection = self.files_listbox.curselection()
            if not selection:
                return
                
            filename = self.files_listbox.get(selection[0])
            review_path = PDF_TXT_DIR / "needs_review" / filename
            
            if not review_path.exists():
                messagebox.showerror("File Not Found", f"The file {filename} was not found.")
                return
                
            self.file_info = {"txt_path": review_path}
            self.load_text_file()
            self.status_var.set(f"Loaded file: {filename}")
        except Exception as e:
            self.status_var.set(f"Error loading file: {e}")
            logger.error(f"Error loading file: {e}")

    def load_patterns_from_config(self):
        """Dynamically loads the specified pattern list from the custom_patterns.py file."""
        try:
            self.pattern_listbox.delete(0, tk.END)
            patterns_to_load = []
            
            # Create file if it doesn't exist
            if not self.custom_patterns_path.exists():
                with open(self.custom_patterns_path, 'w', encoding='utf-8') as f:
                    f.write(f"# custom_patterns.py\n# This file stores user-defined regex patterns.\n\n{self.pattern_name} = [\n]\n")
                self.status_var.set("Created new custom_patterns.py file")
                
            try:
                import custom_patterns as custom_module
                importlib.reload(custom_module)
                patterns_to_load = getattr(custom_module, self.pattern_name, [])
            except (ImportError, SyntaxError) as e:
                self.status_var.set(f"Error loading patterns: {e}")
                logger.error(f"Error loading patterns: {e}")
                
            for pattern in patterns_to_load:
                self.pattern_listbox.insert(tk.END, pattern)
                
            self.status_var.set(f"Loaded {len(patterns_to_load)} patterns")
        except Exception as e:
            self.status_var.set(f"Unexpected error: {e}")
            logger.error(f"Unexpected error in load_patterns_from_config: {e}")
    
    def save_patterns_to_config(self):
        """Re-writes all pattern lists into the custom_patterns.py file correctly."""
        try:
            all_patterns_in_listbox = self.pattern_listbox.get(0, tk.END)
            msg = f"This will save {len(all_patterns_in_listbox)} patterns to the {self.pattern_name} list in custom_patterns.py.\n\nAre you sure?"
            if not messagebox.askyesno("Confirm Save", msg, parent=self):
                return

            all_lists_to_save = {self.pattern_name: list(all_patterns_in_listbox)}
            all_possible_pattern_names = ["MODEL_PATTERNS", "QA_NUMBER_PATTERNS", "PART_NUMBER_PATTERNS"]
            
            try:
                import custom_patterns as custom_module
                importlib.reload(custom_module)
                for name in all_possible_pattern_names:
                    if name != self.pattern_name:
                        if name not in all_lists_to_save:
                            all_lists_to_save[name] = getattr(custom_module, name, [])
            except (ImportError, SyntaxError) as e:
                logger.warning(f"Could not import existing patterns: {e}")

            file_content = "# custom_patterns.py\n# This file stores user-defined regex patterns.\n"
            
            for name, patterns in all_lists_to_save.items():
                file_content += f"\n{name} = [\n"
                for pattern in patterns:
                    safe_pattern = pattern.replace("'", "\\'")
                    file_content += f"    r'{safe_pattern}',\n"
                file_content += "]\n"
            
            # Make a backup of the existing file
            if self.custom_patterns_path.exists():
                backup_path = self.custom_patterns_path.with_suffix('.py.bak')
                import shutil
                shutil.copy2(self.custom_patterns_path, backup_path)
            
            self.custom_patterns_path.write_text(file_content, encoding='utf-8')
            messagebox.showinfo("Success", "Custom patterns saved successfully!\nChanges will apply on the next run.", parent=self)
            self.status_var.set("Patterns saved successfully")
        except Exception as e:
            error_msg = f"Could not save patterns to file: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            messagebox.showerror("Save Failed", f"{error_msg}", parent=self)
            self.status_var.set(f"Save failed: {e}")

    def update_pattern_in_list(self):
        """Updates or adds a pattern to the listbox."""
        try:
            new_pattern = self.pattern_entry.get().strip()
            if not new_pattern:
                messagebox.showwarning("Input Error", "Test/Edit Pattern box is empty.", parent=self)
                return
                
            selection_indices = self.pattern_listbox.curselection()
            if not selection_indices:
                self.pattern_listbox.insert(tk.END, new_pattern)
                self.status_var.set(f"Added new pattern: {new_pattern}")
            else:
                idx = selection_indices[0]
                self.pattern_listbox.delete(idx)
                self.pattern_listbox.insert(idx, new_pattern)
                self.status_var.set(f"Updated pattern at position {idx+1}")
        except Exception as e:
            self.status_var.set(f"Error updating pattern: {e}")
            logger.error(f"Error updating pattern: {e}")

    def on_pattern_select(self, event):
        """Handles selecting a pattern from the listbox."""
        try:
            selection_indices = self.pattern_listbox.curselection()
            if not selection_indices:
                self.remove_btn.config(state=tk.DISABLED)
                self.pattern_entry.delete(0, tk.END)
                return
            selected_pattern = self.pattern_listbox.get(selection_indices[0])
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, selected_pattern)
            self.remove_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Selected pattern: {selected_pattern}")
        except Exception as e:
            self.status_var.set(f"Error selecting pattern: {e}")
            logger.error(f"Error selecting pattern: {e}")

    def add_pattern(self):
        """Adds a new pattern to the listbox."""
        try:
            new_pattern = self.pattern_entry.get().strip()
            if new_pattern:
                self.pattern_listbox.insert(tk.END, new_pattern)
                self.pattern_entry.delete(0, tk.END)
                self.status_var.set(f"Added new pattern: {new_pattern}")
            else:
                messagebox.showwarning("Input Error", "Test/Edit Pattern box is empty. Cannot add.", parent=self)
        except Exception as e:
            self.status_var.set(f"Error adding pattern: {e}")
            logger.error(f"Error adding pattern: {e}")

    def remove_pattern(self):
        """Removes the selected pattern from the listbox."""
        try:
            selection_indices = self.pattern_listbox.curselection()
            if not selection_indices:
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to remove the selected pattern?", parent=self):
                selected_pattern = self.pattern_listbox.get(selection_indices[0])
                self.pattern_listbox.delete(selection_indices[0])
                self.on_pattern_select(None)  # Reset selection
                self.status_var.set(f"Removed pattern: {selected_pattern}")
        except Exception as e:
            self.status_var.set(f"Error removing pattern: {e}")
            logger.error(f"Error removing pattern: {e}")

    def test_pattern(self):
        """Tests the current pattern against the loaded text."""
        try:
            self.pdf_text.tag_remove("highlight", "1.0", "end")
            pattern_str = self.pattern_entry.get()
            
            if not pattern_str:
                messagebox.showwarning("Warning", "Test Pattern box cannot be empty.", parent=self)
                return
                
            content = self.pdf_text.get("1.0", "end")
            matches = list(re.finditer(pattern_str, content, re.IGNORECASE))
            
            if not matches:
                messagebox.showinfo("No Matches", "The pattern did not find any matches in the text.", parent=self)
                self.status_var.set("Pattern test: No matches found")
                return
                
            for match in matches:
                start, end = match.span()
                self.pdf_text.tag_add("highlight", f"1.0+{start}c", f"1.0+{end}c")
                
            self.pdf_text.see(f"1.0+{matches[0].start()-100}c")
            messagebox.showinfo("Success!", f"Found {len(matches)} match(es).", parent=self)
            self.status_var.set(f"Pattern test: Found {len(matches)} matches")
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"The regular expression is invalid:\n{e}", parent=self)
            self.status_var.set(f"Invalid regex pattern: {e}")
        except Exception as e:
            logger.error(f"Error testing pattern: {e}")
            self.status_var.set(f"Error testing pattern: {e}")
            
    def on_suggest_pattern(self):
        """Generates a pattern from the selected text."""
        try:
            try:
                selected_text = self.pdf_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showwarning("No Selection", "Please highlight text to generate a pattern.", parent=self)
                return
                
            if not selected_text or not selected_text.strip():
                messagebox.showwarning("No Selection", "Please highlight text to generate a pattern.", parent=self)
                return
                
            suggested_pattern = generate_regex_from_sample(selected_text)
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, suggested_pattern)
            messagebox.showinfo("Pattern Suggested", "A pattern has been generated in the 'Test / Edit' box.", parent=self)
            self.status_var.set(f"Pattern suggested from: {selected_text[:20]}...")
        except Exception as e:
            logger.error(f"Error suggesting pattern: {e}")
            self.status_var.set(f"Error suggesting pattern: {e}")
            
    def load_text_file(self):
        """Loads the text from the specified file."""
        try:
            self.pdf_text.config(state=tk.NORMAL)
            self.pdf_text.delete("1.0", tk.END)
            
            if self.file_info and "txt_path" in self.file_info:
                txt_path = self.file_info["txt_path"]
                
                if not Path(txt_path).exists():
                    self.pdf_text.insert("1.0", f"Error: File {txt_path} not found.")
                    self.pdf_text.config(state=tk.DISABLED)
                    self.suggest_btn.config(state=tk.DISABLED)
                    self.test_btn.config(state=tk.DISABLED)
                    return
                    
                with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    
                self.pdf_text.insert("1.0", content)
                self.suggest_btn.config(state=tk.NORMAL)
                self.test_btn.config(state=tk.NORMAL)
                self.status_var.set(f"Loaded file: {Path(txt_path).name}")
            else:
                self.pdf_text.insert("1.0", "No file selected. Please select a file from the 'Review Files' list.")
                self.suggest_btn.config(state=tk.DISABLED)
                self.test_btn.config(state=tk.DISABLED)
                
        except Exception as e:
            error_msg = f"Failed to load text file: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.pdf_text.insert("1.0", f"Error: {error_msg}")
            self.pdf_text.config(state=tk.DISABLED)
            self.suggest_btn.config(state=tk.DISABLED)
            self.test_btn.config(state=tk.DISABLED)
            self.status_var.set(f"Error loading file: {e}")