# start_tool.py
# Version: 33.0.0
# Last modified: 2025-07-06
# This is the new, official way to start the application.

import sys
import subprocess
from pathlib import Path
import logging
import time

# --- Color and Style Configuration ---
# Attempt to import and initialize colorama for styled terminal output
try:
    import colorama
    colorama.init(autoreset=True)
    C_GREEN = colorama.Fore.GREEN
    C_YELLOW = colorama.Fore.YELLOW
    C_RED = colorama.Fore.RED
    C_CYAN = colorama.Fore.CYAN
    C_RESET = colorama.Style.RESET_ALL
except ImportError:
    # If colorama is not installed, use empty strings as placeholders
    C_GREEN = C_YELLOW = C_RED = C_CYAN = C_RESET = ""

# --- Logging and Script Configuration ---
VENV_DIR = Path(__file__).parent / "venv"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
LOG_FILE = Path(__file__).parent / "logs" / "startup.log"
MAIN_APP_SCRIPT = Path(__file__).parent / "kyo_qa_tool_app.py"

LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
                              logging.StreamHandler(sys.stdout)])

def get_python_executable():
    """Gets the path to the Python executable inside the virtual environment."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def print_header():
    """Prints the application header with color."""
    header = f"""
     {C_RED}__  __ __   ____
   | |/ // /  / __ \\
   |   // /  / /_/ /
  /   |/ /_ / ____/
 /_/|_/____/_/{C_RESET}

====================================================
       KYO QA ServiceNow Knowledge Tool
====================================================
"""
    print(header)

def execute_command(command, description):
    """Executes a command and streams its output for better feedback."""
    logging.info(description)
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace')
        for line in iter(process.stdout.readline, ''):
            print(f"   > {line.strip()}")
        process.wait()
        if process.returncode != 0:
            logging.error(f"{C_RED}Command failed with exit code {process.returncode}{C_RESET}")
            return False
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.error(f"{C_RED}Failed to execute command: {e}{C_RESET}")
        return False

def setup_environment():
    """Creates a virtual environment and installs dependencies."""
    if not (VENV_DIR.exists() and (VENV_DIR / "pyvenv.cfg").exists()):
        logging.info("Creating virtual environment...")
        execute_command([sys.executable, "-m", "venv", str(VENV_DIR)], f"{C_CYAN}[INFO] Creating venv folder...{C_RESET}")
    else:
        logging.info(f"{C_GREEN}[OK] Virtual environment already exists.{C_RESET}")

    python_venv = get_python_executable()
    
    # Automatically update pip
    logging.info(f"{C_CYAN}[INFO] Checking for pip updates...{C_RESET}")
    execute_command([str(python_venv), "-m", "pip", "install", "--upgrade", "pip"], f"{C_CYAN}[INFO] Upgrading pip...{C_RESET}")
    
    # Ensure colorama is installed first for a better experience
    execute_command([str(python_venv), "-m", "pip", "install", "colorama"], f"{C_CYAN}[INFO] Ensuring colorama is installed...{C_RESET}")
    
    logging.info("Verifying and installing dependencies from requirements.txt...")
    command = [str(python_venv), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    if not execute_command(command, f"{C_CYAN}[INFO] Installing packages...{C_RESET}"):
        logging.error(f"{C_RED}Failed to install dependencies.{C_RESET}")
        return False

    logging.info(f"{C_GREEN}[SUCCESS] Environment is ready.{C_RESET}")
    return True

def launch_application():
    """Launches the main GUI application."""
    logging.info(f"\n{C_CYAN}--- Launching Application ---{C_RESET}")
    logging.info("[INFO] A console window will remain open for stability. You can minimize it.")
    try:
        result = subprocess.run([get_python_executable(), str(MAIN_APP_SCRIPT)], capture_output=True,
                                text=True, encoding='utf-8', errors='replace')
        if result.stdout: logging.info("Application output:\n" + result.stdout)
        if result.stderr: logging.error("Application errors:\n" + result.stderr)
        if result.returncode != 0:
             logging.error(f"\n{C_RED}--- APPLICATION CRASHED ---{C_RESET}")
             logging.error("The application closed unexpectedly. Review any error messages above.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while launching the application: {e}")

if __name__ == "__main__":
    print_header()
    if setup_environment():
        launch_application()
    else:
        logging.error(f"\n{C_RED}[FAIL] Setup failed. Please check the logs above for details.{C_RESET}")
