#!/usr/bin/env python3
# KYO QA Tool Diagnostic and Repair Utility
# Run this to diagnose and fix common issues with the KYO QA ServiceNow Knowledge Tool

import os
import sys
import shutil
import subprocess
from pathlib import Path
import importlib.util
import platform
import traceback
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# --- Configuration ---
ROOT_DIR = Path(__file__).parent
VENV_DIR = ROOT_DIR / "venv"
LOG_DIR = ROOT_DIR / "logs"
OUTPUT_DIR = ROOT_DIR / "output"
PDF_TXT_DIR = ROOT_DIR / "PDF_TXT"
CACHE_DIR = ROOT_DIR / ".cache"
ASSETS_DIR = ROOT_DIR / "assets"
REVIEW_DIR = PDF_TXT_DIR / "needs_review"
REQUIRED_FOLDERS = [LOG_DIR, OUTPUT_DIR, PDF_TXT_DIR, CACHE_DIR, ASSETS_DIR, REVIEW_DIR]

# --- UI Colors ---
COLORS = {
    "bg": "#f0f0f0",
    "header_bg": "#DA291C",  # Kyocera Red
    "header_fg": "white",
    "pass": "#107C10",
    "fail": "#DA291C", 
    "warn": "#FFA500",
    "info": "#0078D4"
}

# --- Main Application Class ---
class DiagnosticTool:
    def __init__(self, root):
        self.root = root
        self.root.title("KYO QA Tool Diagnostic")
        self.root.geometry("800x600")
        self.root.config(bg=COLORS["bg"])
        
        self.setup_ui()
        self.results = {}
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["header_bg"], pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="KYO QA Tool Diagnostic & Repair", 
                 font=("Arial", 16, "bold"), bg=COLORS["header_bg"], 
                 fg=COLORS["header_fg"]).pack()
        
        # Main content area
        content = tk.Frame(self.root, bg=COLORS["bg"], padx=20, pady=10)
        content.pack(fill=tk.BOTH, expand=True)
        
        # System info
        info_frame = tk.LabelFrame(content, text="System Information", bg=COLORS["bg"], padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        self.system_info = tk.Text(info_frame, height=4, wrap=tk.WORD, bg="white", font=("Consolas", 9))
        self.system_info.pack(fill=tk.X)
        
        # Tests frame
        tests_frame = tk.LabelFrame(content, text="Diagnostic Tests", bg=COLORS["bg"], padx=10, pady=10)
        tests_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollable canvas for tests
        canvas = tk.Canvas(tests_frame, bg=COLORS["bg"])
        scrollbar = ttk.Scrollbar(tests_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tests_container = scrollable_frame
        
        # Action buttons
        button_frame = tk.Frame(content, bg=COLORS["bg"], pady=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Run All Tests", command=self.run_all_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fix Problems", command=self.fix_all_problems).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Report", command=self.create_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Initialize test cards
        self.test_cards = {}
        self.create_test_cards()
        
    def create_test_cards(self):
        tests = [
            ("folder_structure", "Folder Structure", "Checks if all required folders exist"),
            ("python_version", "Python Version", "Verifies Python 3.9+ is installed"),
            ("tesseract_check", "Tesseract OCR", "Checks if Tesseract OCR is available"),
            ("venv_check", "Virtual Environment", "Verifies venv is properly configured"),
            ("dependencies_check", "Dependencies", "Checks if all required packages are installed"),
            ("launcher_check", "Launcher Configuration", "Verifies START.bat configuration"),
            ("file_permissions", "File Permissions", "Checks write permissions for output folders"),
            ("assets_check", "Assets/Icons", "Verifies required icons are present"),
            ("syntax_check", "Syntax Check", "Checks for syntax errors in key files"),
            ("config_check", "Configuration", "Validates configuration settings")
        ]
        
        for test_id, title, description in tests:
            self.create_test_card(test_id, title, description)
    
    def create_test_card(self, test_id, title, description):
        card = tk.Frame(self.tests_container, relief=tk.GROOVE, borderwidth=1)
        card.pack(fill=tk.X, pady=5, padx=5)
        
        header = tk.Frame(card)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        status_label = tk.Label(header, text="●", fg="gray")
        status_label.pack(side=tk.LEFT)
        
        tk.Label(header, text=title, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        details_frame = tk.Frame(card)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(details_frame, text=description, anchor="w").pack(fill=tk.X, pady=2)
        
        result_var = tk.StringVar(value="Not tested")
        result_label = tk.Label(details_frame, textvariable=result_var, anchor="w")
        result_label.pack(fill=tk.X, pady=2)
        
        fix_button = ttk.Button(details_frame, text="Fix", state=tk.DISABLED)
        fix_button.pack(anchor="e", pady=5)
        
        self.test_cards[test_id] = {
            "card": card,
            "status": status_label,
            "result": result_var,
            "fix_button": fix_button
        }
    
    def update_test_status(self, test_id, status, message, can_fix=False):
        card = self.test_cards.get(test_id)
        if not card:
            return
        
        status_colors = {
            "pass": COLORS["pass"],
            "fail": COLORS["fail"],
            "warn": COLORS["warn"],
            "info": COLORS["info"]
        }
        
        card["status"].config(fg=status_colors.get(status, "gray"))
        card["result"].set(message)
        
        # Store the result for reporting
        self.results[test_id] = {
            "status": status,
            "message": message,
            "can_fix": can_fix
        }
        
        # Enable/disable fix button
        if can_fix:
            fix_fn = getattr(self, f"fix_{test_id}", None)
            if fix_fn:
                card["fix_button"].config(
                    state=tk.NORMAL, 
                    command=lambda t=test_id, f=fix_fn: self.run_fix(t, f)
                )
        else:
            card["fix_button"].config(state=tk.DISABLED)
    
    def run_fix(self, test_id, fix_fn):
        try:
            result = fix_fn()
            if result:
                self.update_test_status(test_id, "pass", f"Fixed: {result}")
            else:
                self.update_test_status(test_id, "warn", "Fix attempted but could not verify results")
        except Exception as e:
            self.update_test_status(test_id, "fail", f"Fix failed: {str(e)}")
    
    def run_all_tests(self):
        # Collect system information
        self.collect_system_info()
        
        # Run all tests
        self.test_folder_structure()
        self.test_python_version()
        self.test_tesseract()
        self.test_venv()
        self.test_dependencies()
        self.test_launcher()
        self.test_file_permissions()
        self.test_assets()
        self.test_syntax()
        self.test_config()
        
        messagebox.showinfo("Tests Complete", "All diagnostic tests have been completed.")
    
    def fix_all_problems(self):
        fixable_tests = [test_id for test_id, result in self.results.items() 
                          if result.get("can_fix", False)]
        
        if not fixable_tests:
            messagebox.showinfo("No Fixable Issues", 
                               "No fixable issues were found. Run tests first or all tests passed!")
            return
        
        for test_id in fixable_tests:
            fix_fn = getattr(self, f"fix_{test_id}", None)
            if fix_fn:
                self.run_fix(test_id, fix_fn)
        
        messagebox.showinfo("Fixes Applied", 
                           f"{len(fixable_tests)} issue(s) have been fixed. Re-run tests to verify.")
    
    def create_report(self):
        report_path = LOG_DIR / f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        LOG_DIR.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("KYO QA Tool Diagnostic Report\n")
            f.write("=============================\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # System info
            f.write("System Information:\n")
            f.write("------------------\n")
            f.write(self.system_info.get("1.0", tk.END))
            f.write("\n")
            
            # Test results
            f.write("Test Results:\n")
            f.write("------------\n")
            
            for test_id, data in self.results.items():
                status = data.get("status", "unknown")
                message = data.get("message", "No information")
                status_text = {
                    "pass": "PASS",
                    "fail": "FAIL",
                    "warn": "WARNING",
                    "info": "INFO"
                }.get(status, "UNKNOWN")
                
                title = next((t[1] for t in [
                    ("folder_structure", "Folder Structure"),
                    ("python_version", "Python Version"),
                    ("tesseract_check", "Tesseract OCR"),
                    ("venv_check", "Virtual Environment"),
                    ("dependencies_check", "Dependencies"),
                    ("launcher_check", "Launcher Configuration"),
                    ("file_permissions", "File Permissions"),
                    ("assets_check", "Assets/Icons"),
                    ("syntax_check", "Syntax Check"),
                    ("config_check", "Configuration")
                ] if t[0] == test_id), test_id)
                
                f.write(f"[{status_text}] {title}: {message}\n")
            
            f.write("\nEnd of Report\n")
        
        messagebox.showinfo("Report Created", f"Diagnostic report created at:\n{report_path}")
        
        try:
            # Try to open the report file with the default application
            if os.name == 'nt':  # Windows
                os.startfile(report_path)
            elif os.name == 'posix':  # macOS, Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', report_path])
                else:  # Linux
                    subprocess.call(['xdg-open', report_path])
        except:
            pass  # Ignore if we can't open the file
    
    def collect_system_info(self):
        self.system_info.delete("1.0", tk.END)
        
        # Get system info
        system_info = [
            f"OS: {platform.system()} {platform.release()} ({platform.platform()})",
            f"Python: {platform.python_version()} ({platform.python_implementation()})",
            f"Machine: {platform.machine()}",
            f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        self.system_info.insert("1.0", "\n".join(system_info))
    
    # --- Test Implementations ---
    
    def test_folder_structure(self):
        missing_folders = []
        
        for folder in REQUIRED_FOLDERS:
            if not folder.exists():
                missing_folders.append(str(folder.relative_to(ROOT_DIR)))
        
        if missing_folders:
            self.update_test_status(
                "folder_structure", 
                "fail", 
                f"Missing folders: {', '.join(missing_folders)}",
                can_fix=True
            )
        else:
            self.update_test_status(
                "folder_structure", 
                "pass", 
                "All required folders exist"
            )
    
    def fix_folder_structure(self):
        created = []
        
        for folder in REQUIRED_FOLDERS:
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
                created.append(str(folder.relative_to(ROOT_DIR)))
        
        return f"Created folders: {', '.join(created)}" if created else "No folders needed creation"
    
    def test_python_version(self):
        if sys.version_info >= (3, 9):
            self.update_test_status(
                "python_version",
                "pass",
                f"Python {sys.version.split()[0]} meets minimum requirement (3.9+)"
            )
        else:
            self.update_test_status(
                "python_version",
                "fail",
                f"Python {sys.version.split()[0]} is below minimum requirement (3.9+)"
            )
    
    def test_tesseract(self):
        try:
            # Try to import pytesseract
            import pytesseract
            
            # Try to find Tesseract installation
            tesseract_path = None
            
            # Check portable Tesseract
            portable_path = ROOT_DIR / "tesseract" / "tesseract.exe"
            if portable_path.exists():
                tesseract_path = portable_path
            
            # Check common install locations
            if not tesseract_path:
                common_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        tesseract_path = path
                        break
            
            # Check if it's in PATH
            if not tesseract_path:
                try:
                    output = subprocess.check_output(["tesseract", "--version"], 
                                                     stderr=subprocess.STDOUT,
                                                     universal_newlines=True)
                    if "tesseract" in output.lower():
                        tesseract_path = "In system PATH"
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
            
            if tesseract_path:
                self.update_test_status(
                    "tesseract_check",
                    "pass",
                    f"Tesseract OCR found: {tesseract_path}"
                )
            else:
                self.update_test_status(
                    "tesseract_check",
                    "fail",
                    "Tesseract OCR not found. OCR functionality will be limited.",
                    can_fix=True
                )
        except ImportError:
            self.update_test_status(
                "tesseract_check",
                "fail",
                "pytesseract module not installed. Install via pip install pytesseract.",
                can_fix=True if VENV_DIR.exists() else False
            )
        except Exception as e:
            self.update_test_status(
                "tesseract_check",
                "fail",
                f"Error checking Tesseract: {str(e)}"
            )
    
    def fix_tesseract(self):
        # This would ideally download and install Tesseract, but that's complex
        # So we'll just provide instructions
        messagebox.showinfo(
            "Tesseract Installation", 
            "To install Tesseract OCR:\n\n"
            "1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Run the installer and check 'Add to PATH'\n"
            "3. Restart the diagnostic tool after installation"
        )
        return "Provided installation instructions"
    
    def test_venv(self):
        venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == 'nt' else VENV_DIR / "bin" / "python"
        
        if not VENV_DIR.exists():
            self.update_test_status(
                "venv_check",
                "fail",
                "Virtual environment not found",
                can_fix=True
            )
            return
        
        if not venv_python.exists():
            self.update_test_status(
                "venv_check",
                "fail",
                "Virtual environment exists but Python interpreter not found",
                can_fix=True
            )
            return
        
        # Check if it's a valid Python interpreter
        try:
            result = subprocess.run(
                [str(venv_python), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.update_test_status(
                "venv_check",
                "pass",
                f"Virtual environment valid: {result.stdout.strip()}"
            )
        except subprocess.SubprocessError:
            self.update_test_status(
                "venv_check",
                "fail",
                "Virtual environment exists but interpreter not working",
                can_fix=True
            )
    
    def fix_venv(self):
        # Remove existing venv if it exists
        if VENV_DIR.exists():
            try:
                shutil.rmtree(VENV_DIR)
            except OSError as e:
                return f"Could not remove existing venv: {str(e)}"
        
        # Create new venv
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(VENV_DIR)],
                check=True,
                capture_output=True
            )
            
            # Install pip
            venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == 'nt' else VENV_DIR / "bin" / "python"
            subprocess.run(
                [str(venv_python), "-m", "ensurepip", "--default-pip"],
                check=True,
                capture_output=True
            )
            
            return "Created new virtual environment"
        except subprocess.SubprocessError as e:
            return f"Failed to create virtual environment: {str(e)}"
    
    def test_dependencies(self):
        if not VENV_DIR.exists():
            self.update_test_status(
                "dependencies_check",
                "warn",
                "Virtual environment not found, skipping dependency check"
            )
            return
        
        requirements_file = ROOT_DIR / "requirements.txt"
        if not requirements_file.exists():
            self.update_test_status(
                "dependencies_check",
                "fail",
                "requirements.txt not found",
                can_fix=True
            )
            return
        
        venv_pip = VENV_DIR / "Scripts" / "pip.exe" if os.name == 'nt' else VENV_DIR / "bin" / "pip"
        if not venv_pip.exists():
            self.update_test_status(
                "dependencies_check",
                "fail",
                "pip not found in virtual environment",
                can_fix=True
            )
            return
        
        # Check installed packages
        try:
            result = subprocess.run(
                [str(venv_pip), "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            installed_packages = result.stdout.lower()
            
            # Check for key packages
            key_packages = ["pandas", "openpyxl", "pymupdf", "pillow", "opencv-python", 
                           "pytesseract", "numpy", "ollama", "colorama"]
            
            missing_packages = []
            for package in key_packages:
                if package.lower() not in installed_packages:
                    missing_packages.append(package)
            
            if missing_packages:
                self.update_test_status(
                    "dependencies_check",
                    "fail",
                    f"Missing packages: {', '.join(missing_packages)}",
                    can_fix=True
                )
            else:
                self.update_test_status(
                    "dependencies_check",
                    "pass",
                    "All key dependencies installed"
                )
        except subprocess.SubprocessError as e:
            self.update_test_status(
                "dependencies_check",
                "fail",
                f"Error checking dependencies: {str(e)}",
                can_fix=True
            )
    
    def fix_dependencies(self):
        requirements_file = ROOT_DIR / "requirements.txt"
        if not requirements_file.exists():
            return "requirements.txt not found, cannot install dependencies"
        
        venv_pip = VENV_DIR / "Scripts" / "pip.exe" if os.name == 'nt' else VENV_DIR / "bin" / "pip"
        if not venv_pip.exists():
            return "pip not found in virtual environment"
        
        try:
            # Update pip first
            subprocess.run(
                [str(venv_pip), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )
            
            # Install requirements
            subprocess.run(
                [str(venv_pip), "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            
            return "Installed dependencies from requirements.txt"
        except subprocess.SubprocessError as e:
            return f"Failed to install dependencies: {str(e)}"
    
    def test_launcher(self):
        start_bat = ROOT_DIR / "START.bat"
        if not start_bat.exists():
            self.update_test_status(
                "launcher_check",
                "fail",
                "START.bat not found",
                can_fix=True
            )
            return
        
        # Check START.bat content
        with open(start_bat, 'r') as f:
            content = f.read().lower()
        
        if "python run.py" in content and not (ROOT_DIR / "run.py").exists():
            self.update_test_status(
                "launcher_check",
                "fail",
                "START.bat references run.py but file not found",
                can_fix=True
            )
            return
        
        if "python start_tool.py" not in content and (ROOT_DIR / "start_tool.py").exists():
            self.update_test_status(
                "launcher_check",
                "warn",
                "START.bat doesn't call start_tool.py directly",
                can_fix=True
            )
            return
        
        self.update_test_status(
            "launcher_check",
            "pass",
            "Launcher configuration appears correct"
        )
    
    def fix_launcher(self):
        start_bat = ROOT_DIR / "START.bat"
        
        # Create a new START.bat that directly calls start_tool.py
        with open(start_bat, 'w') as f:
            f.write("@echo off\n")
            f.write("title KYO QA Tool Launcher\n")
            f.write("python start_tool.py")
        
        return "Fixed START.bat to call start_tool.py directly"
    
    def test_file_permissions(self):
        problem_folders = []
        
        for folder in [OUTPUT_DIR, LOG_DIR, PDF_TXT_DIR, CACHE_DIR]:
            if not folder.exists():
                continue
            
            # Test writing to the folder
            test_file = folder / f"permission_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.tmp"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()  # Delete the test file
            except (PermissionError, OSError):
                problem_folders.append(str(folder.relative_to(ROOT_DIR)))
        
        if problem_folders:
            self.update_test_status(
                "file_permissions",
                "fail",
                f"Write permission issues in folders: {', '.join(problem_folders)}",
                can_fix=True
            )
        else:
            self.update_test_status(
                "file_permissions",
                "pass",
                "Write permissions OK for all output folders"
            )
    
    def fix_file_permissions(self):
        # This is OS-specific and complex to implement fully
        # We'll provide guidance instead
        messagebox.showinfo(
            "Fix Permissions", 
            "To fix folder permissions:\n\n"
            "1. Right-click the application folder\n"
            "2. Select Properties > Security\n"
            "3. Ensure your user account has Read/Write permissions\n"
            "4. You may need administrator rights to change permissions"
        )
        return "Provided instructions to fix permissions manually"
    
    def test_assets(self):
        if not ASSETS_DIR.exists():
            self.update_test_status(
                "assets_check",
                "fail",
                "Assets folder not found",
                can_fix=True
            )
            return
        
        required_icons = ["start.png", "pause.png", "stop.png", "rerun.png", 
                         "open.png", "browse.png", "patterns.png", "exit.png",
                         "fullscreen.png"]
        
        missing_icons = []
        for icon in required_icons:
            if not (ASSETS_DIR / icon).exists():
                missing_icons.append(icon)
        
        if missing_icons:
            self.update_test_status(
                "assets_check",
                "fail",
                f"Missing icons: {', '.join(missing_icons)}",
                can_fix=True
            )
        else:
            self.update_test_status(
                "assets_check",
                "pass",
                "All required icons found in assets folder"
            )
    
    def fix_assets(self):
        ASSETS_DIR.mkdir(exist_ok=True)
        
        # Create simple placeholder icons (1x1 pixels)
        icons = ["start.png", "pause.png", "stop.png", "rerun.png", 
                "open.png", "browse.png", "patterns.png", "exit.png",
                "fullscreen.png"]
        
        try:
            from PIL import Image
            
            created = []
            for icon in icons:
                if not (ASSETS_DIR / icon).exists():
                    img = Image.new('RGBA', (16, 16), color=(200, 200, 200, 255))
                    img.save(ASSETS_DIR / icon)
                    created.append(icon)
            
            return f"Created placeholder icons: {', '.join(created)}" if created else "No icons needed creation"
        except ImportError:
            # If PIL is not available, create empty files
            created = []
            for icon in icons:
                if not (ASSETS_DIR / icon).exists():
                    with open(ASSETS_DIR / icon, 'wb') as f:
                        f.write(b'')  # Empty file
                    created.append(icon)
            
            return f"Created empty icon files (install Pillow for proper icons): {', '.join(created)}" if created else "No icons needed creation"
    
    def test_syntax(self):
        key_files = [
            "kyo_qa_tool_app.py",
            "start_tool.py",
            "processing_engine.py",
            "ocr_utils.py",
            "data_harvesters.py",
            "excel_generator.py",
            "file_utils.py",
            "logging_utils.py",
            "custom_exceptions.py",
            "config.py"
        ]
        
        syntax_errors = []
        
        for file in key_files:
            file_path = ROOT_DIR / file
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Check syntax
                compile(source, file, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file}: {str(e)}")
            except Exception as e:
                syntax_errors.append(f"{file}: Error reading file: {str(e)}")
        
        if syntax_errors:
            self.update_test_status(
                "syntax_check",
                "fail",
                f"Syntax errors found: {'; '.join(syntax_errors)}",
                can_fix=False  # Syntax errors need manual fixing
            )
        else:
            self.update_test_status(
                "syntax_check",
                "pass",
                "No syntax errors found in key files"
            )
    
    def test_config(self):
        config_file = ROOT_DIR / "config.py"
        if not config_file.exists():
            self.update_test_status(
                "config_check",
                "fail",
                "config.py not found",
                can_fix=True
            )
            return
        
        try:
            spec = importlib.util.spec_from_file_location("config", config_file)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            # Check for required variables
            required_vars = [
                "BASE_DIR", "OUTPUT_DIR", "LOGS_DIR", "PDF_TXT_DIR", "CACHE_DIR",
                "BRAND_COLORS", "MODEL_PATTERNS", "QA_NUMBER_PATTERNS"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not hasattr(config, var):
                    missing_vars.append(var)
            
            if missing_vars:
                self.update_test_status(
                    "config_check",
                    "fail",
                    f"Missing configuration variables: {', '.join(missing_vars)}",
                    can_fix=True
                )
                return
            
            # Check Path objects
            path_vars = ["BASE_DIR", "OUTPUT_DIR", "LOGS_DIR", "PDF_TXT_DIR", "CACHE_DIR"]
            
            for var in path_vars:
                value = getattr(config, var)
                if not isinstance(value, Path):
                    self.update_test_status(
                        "config_check",
                        "fail",
                        f"Configuration variable {var} is not a Path object",
                        can_fix=True
                    )
                    return
            
            self.update_test_status(
                "config_check",
                "pass",
                "Configuration appears valid"
            )
        except Exception as e:
            self.update_test_status(
                "config_check",
                "fail",
                f"Error validating configuration: {str(e)}",
                can_fix=True
            )
    
    def fix_config(self):
        config_file = ROOT_DIR / "config.py"
        
        # Basic config file template
        config_template = """# config.py
from pathlib import Path

# --- DIRECTORY CONFIGURATION ---
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
PDF_TXT_DIR = BASE_DIR / "PDF_TXT"
CACHE_DIR = BASE_DIR / ".cache"
ASSETS_DIR = BASE_DIR / "assets" # For icons

# --- BRANDING AND UI ---
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
    # Status bar background colors
    "status_default_bg": "#F8F8F8",
    "status_processing_bg": "#DDEEFF",
    "status_ocr_bg": "#E6F7FF",
    "status_ai_bg": "#F9F0FF",
}

# --- DATA PROCESSING RULES ---
EXCLUSION_PATTERNS = ["CVE-", "CWE-", "TK-"]
MODEL_PATTERNS = [
    r'\\bTASKalfa\\s*[\\w-]+\\b',
    r'\\bECOSYS\\s*[\\w-]+\\b',
    r'\\b(PF|DF|MK|AK|DP|BF|JS)-\\d+[\\w-]*\\b',
]
QA_NUMBER_PATTERNS = [r'\\bQA[-_]?[\\w-]+', r'\\bSB[-_]?[\\w-]+']
UNWANTED_AUTHORS = ["Knowledge Import"]
STANDARDIZATION_RULES = {"TASKalfa-": "TASKalfa ", "ECOSYS-": "ECOSYS "}

# --- EXCEL MAPPING ---
META_COLUMN_NAME = "Meta"
AUTHOR_COLUMN_NAME = "Author"
DESCRIPTION_COLUMN_NAME = "Short description"
STATUS_COLUMN_NAME = "Processing Status"
"""
        
        # Backup existing config if it exists
        if config_file.exists():
            backup_file = config_file.with_suffix('.py.bak')
            try:
                shutil.copy(config_file, backup_file)
            except:
                pass
        
        # Write new config
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_template)
        
        return "Created/restored default config.py file"

# --- Main Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosticTool(root)
    root.mainloop()
