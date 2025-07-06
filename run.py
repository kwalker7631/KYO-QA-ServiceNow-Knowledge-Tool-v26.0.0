# run.py
# Version: 26.0.0
# Last modified: 2025-07-06
# Application launcher with dependency setup and error handling

import sys
import subprocess
from pathlib import Path
import shutil
import time
import threading
import logging
import os
import traceback

# Only try to import error_reporter after dependencies are installed
def safe_import_error_reporter():
    """Safely import error_reporter module, returning None if not available."""
    try:
        from error_reporter import report_error_to_ai
        return report_error_to_ai
    except ImportError:
        return None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(module)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --- Configuration ---
VENV_DIR = Path(__file__).parent / "venv"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
MAIN_APP_SCRIPT = Path(__file__).parent / "kyo_qa_tool_app.py"
MIN_PYTHON_VERSION = (3, 9)

# --- ANSI Colors for "Bling" ---
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Required packages (updated list) ---
REQUIRED_PACKAGES = [
    "pandas", 
    "openpyxl", 
    "PyMuPDF", 
    "pytesseract", 
    "colorama", 
    "python-dateutil", 
    "Pillow", 
    "opencv-python",
    "numpy"
]

def print_header():
    """Prints the stylized ASCII art header."""
    header = f"""
{Colors.BLUE}
   __  __ __   ____
  | |/ // /  / __ \\
  |   // /  / /_/ /
 /   |/ /_ / ____/
/_/|_/____/_/
{Colors.ENDC}
====================================================
       {Colors.BOLD}KYO QA ServiceNow Knowledge Tool{Colors.ENDC}
====================================================
"""
    print(header)

def run_command_with_spinner(command, message):
    """Runs a command silently while showing a spinner."""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    process_done = threading.Event()

    def spin():
        i = 0
        while not process_done.is_set():
            sys.stdout.write(f"\r{Colors.YELLOW}{spinner_chars[i % len(spinner_chars)]}{Colors.ENDC} {message}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)

    spinner_thread = threading.Thread(target=spin, daemon=True)
    spinner_thread.start()

    try:
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process_done.set()
        spinner_thread.join()
        sys.stdout.write(f"\r{Colors.GREEN}✓{Colors.ENDC} {message}... Done.\n")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        process_done.set()
        spinner_thread.join()
        sys.stdout.write(f"\r{Colors.RED}✗{Colors.ENDC} {message}... Failed.\n")
        return False

def get_git_commit() -> str:
    """Return current git commit hash if available."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent).decode().strip()
    except Exception:
        return "unknown"

def get_venv_python_path():
    """Gets the path to the Python executable in the virtual environment."""
    return VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "python"

def ensure_pip(python_path):
    """Ensures pip is installed and working."""
    try:
        subprocess.check_call([str(python_path), "-m", "pip", "--version"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Colors.YELLOW}Pip not found, installing...{Colors.ENDC}")
        return run_command_with_spinner(
            [str(python_path), "-m", "ensurepip", "--default-pip"], 
            "Installing pip"
        )

def setup_environment():
    """Checks Python version, creates venv, and installs dependencies."""
    try:
        print_header()

        if sys.version_info < MIN_PYTHON_VERSION:
            print(
                f"{Colors.RED}✗ Error: Python {'.'.join(map(str, MIN_PYTHON_VERSION))}+ is required.{Colors.ENDC}"
            )
            return False

        venv_python = get_venv_python_path()
        if not (VENV_DIR.exists() and venv_python.exists()):
            print("[INFO] Creating virtual environment...")
            if VENV_DIR.exists():
                shutil.rmtree(VENV_DIR)
            if not run_command_with_spinner([sys.executable, "-m", "venv", str(VENV_DIR)], "Creating venv folder"):
                return False

            if not ensure_pip(venv_python):
                return False

            print("[INFO] Installing dependencies (this may take a few minutes)...")
            if not run_command_with_spinner([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], "Installing packages"):
                print(f"{Colors.YELLOW}Bulk installation failed. Trying individual packages...{Colors.ENDC}")
                
                # First install numpy as it's needed by opencv-python
                run_command_with_spinner([str(venv_python), "-m", "pip", "install", "numpy"], "Installing numpy")
                
                for package in REQUIRED_PACKAGES:
                    if not run_command_with_spinner([str(venv_python), "-m", "pip", "install", package], f"Installing {package}"):
                        print(f"{Colors.YELLOW}Failed to install {package}. This may affect functionality.{Colors.ENDC}")
                
                # Try to install remaining packages from requirements
                run_command_with_spinner([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], 
                                         "Installing remaining packages")
        else:
            print(f"{Colors.GREEN}✓ Virtual environment already exists.{Colors.ENDC}")
            if not run_command_with_spinner([str(venv_python), "-m", "pip", "install", "--quiet", "-r", str(REQUIREMENTS_FILE)], "Verifying dependencies"):
                print(f"{Colors.YELLOW}Warning: Some dependencies may not be properly installed.{Colors.ENDC}")
                # Try installing core packages individually
                for package in REQUIRED_PACKAGES:
                    run_command_with_spinner([str(venv_python), "-m", "pip", "install", "--quiet", package], 
                                            f"Ensuring {package} is installed")

        print(f"{Colors.GREEN}✓ Environment is ready.{Colors.ENDC}")
        return True
    except Exception as exc:
        context = {
            "function": "setup_environment",
            "filename": __file__,
            "lineno": exc.__traceback__.tb_lineno if exc.__traceback__ else 0,
            "commit": get_git_commit(),
        }
        logging.exception("setup_environment failed")
        
        # Try to report error only if dependencies are available
        report_error_to_ai = safe_import_error_reporter()
        if report_error_to_ai:
            report_error_to_ai(exc, context)
        
        raise

def launch_application():
    """Launches the main GUI application and waits for it to close."""
    try:
        print(f"\n{Colors.GREEN}--- Launching Application ---{Colors.ENDC}")
        print("[INFO] A console window will remain open for stability. You can minimize it.")

        venv_python = get_venv_python_path()
        
        # Create a wrapped script to handle ImportError more gracefully
        wrapper_script = """
import sys
import importlib

try:
    import kyo_qa_tool_app
    kyo_qa_tool_app.main()
except ImportError as e:
    module_name = str(e).split("'")[-2] if "'" in str(e) else str(e).split()[-1]
    if module_name:
        print(f"\\nMissing dependency: {module_name}")
        print(f"Attempting to install {module_name}...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"Successfully installed {module_name}, restarting application...")
            # Try to reimport
            if module_name in sys.modules:
                del sys.modules[module_name]
            importlib.import_module(module_name)
            # Now try to run the application again
            import kyo_qa_tool_app
            kyo_qa_tool_app.main()
        except Exception as install_error:
            print(f"Failed to install {module_name}: {install_error}")
            print("\\nPlease run the following command manually:")
            print(f"  {sys.executable} -m pip install {module_name}")
            input("\\nPress Enter to exit...")
    else:
        print(f"\\nImport error: {e}")
        input("\\nPress Enter to exit...")
except Exception as e:
    print(f"\\nApplication error: {e}")
    input("\\nPress Enter to exit...")
"""
        
        # Write the wrapper script to a temporary file
        wrapper_path = Path(__file__).parent / "run_wrapper.py"
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
            
        # Run the application with the wrapper
        subprocess.run([str(venv_python), str(wrapper_path)], check=True)
        
        # Clean up
        if wrapper_path.exists():
            wrapper_path.unlink()
            
        print(f"\n{Colors.GREEN}--- Application Closed ---{Colors.ENDC}")
    except subprocess.CalledProcessError as exc:
        print(f"\n{Colors.RED}--- APPLICATION CRASHED ---{Colors.ENDC}")
        print(f"{Colors.YELLOW}The application closed unexpectedly. Please review any error messages above.{Colors.ENDC}")
        context = {
            "function": "launch_application",
            "filename": __file__,
            "lineno": exc.__traceback__.tb_lineno if exc.__traceback__ else 0,
            "commit": get_git_commit(),
        }
        logging.exception("launch_application crashed")
        
        # Try to report error only if dependencies are available
        report_error_to_ai = safe_import_error_reporter()
        if report_error_to_ai:
            report_error_to_ai(exc, context)
        
        raise
    except FileNotFoundError as exc:
        print(f"\n{Colors.RED}--- LAUNCH FAILED ---{Colors.ENDC}")
        print(f"{Colors.YELLOW}Could not find the application script: {MAIN_APP_SCRIPT}{Colors.ENDC}")
        context = {
            "function": "launch_application",
            "filename": __file__,
            "lineno": exc.__traceback__.tb_lineno if exc.__traceback__ else 0,
            "commit": get_git_commit(),
        }
        logging.exception("launch_application failed")
        
        # Try to report error only if dependencies are available
        report_error_to_ai = safe_import_error_reporter()
        if report_error_to_ai:
            report_error_to_ai(exc, context)
        
        raise

def add_main_function_to_app():
    """Add a main() function to kyo_qa_tool_app.py if it doesn't exist."""
    try:
        app_path = Path(MAIN_APP_SCRIPT)
        content = app_path.read_text(encoding='utf-8')
        
        # Check if main() function already exists
        if "def main():" not in content:
            # Add main function before the if __name__ == "__main__" block
            if "if __name__ == \"__main__\":" in content:
                new_content = content.replace(
                    "if __name__ == \"__main__\":",
                    "def main():\n    app = KyoQAToolApp()\n    app.mainloop()\n\nif __name__ == \"__main__\":"
                )
                app_path.write_text(new_content, encoding='utf-8')
                print(f"{Colors.GREEN}✓ Added main() function to {app_path.name}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.YELLOW}Note: Could not update {app_path.name}: {e}{Colors.ENDC}")

if __name__ == "__main__":
    try:
        if setup_environment():
            # Add main() function to app file if needed
            add_main_function_to_app()
            
            # Only try to initialize error tracker after dependencies are installed
            try:
                import error_tracker
                error_tracker.init_error_tracker()
            except ImportError:
                print(f"{Colors.YELLOW}Note: Error tracking not available (optional dependency){Colors.ENDC}")
            
            launch_application()
    except Exception as exc:
        context = {
            "function": "__main__",
            "filename": __file__,
            "lineno": exc.__traceback__.tb_lineno if exc.__traceback__ else 0,
            "args": sys.argv,
            "commit": get_git_commit(),
        }
        logging.exception("launcher failed")
        
        # Try to report error only if dependencies are available
        report_error_to_ai = safe_import_error_reporter()
        if report_error_to_ai:
            report_error_to_ai(exc, context)
        
        print("\nThe application could not be started. Please check the log files for details.")
        input("\nPress Enter to exit...")
    else:
        print("\nPress Enter to exit the launcher.")
        input()