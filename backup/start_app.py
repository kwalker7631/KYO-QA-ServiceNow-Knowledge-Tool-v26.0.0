# start_tool.py
# Version: 32.3.0
# Last modified: 2025-07-06
# This is the new, official way to start the application.

import sys
import subprocess
from pathlib import Path
import logging

# --- Configuration ---
VENV_DIR = Path(__file__).parent / "venv"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
LOG_FILE = Path(__file__).parent / "logs" / "startup.log"
MAIN_APP_SCRIPT = Path(__file__).parent / "kyo_qa_tool_app.py"

# --- Setup Logging ---
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_python_executable():
    """Gets the path to the Python executable inside the virtual environment."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def print_header():
    """Prints the application header."""
    header = """
     __  __ __   ____
   | |/ // /  / __ \\
   |   // /  / /_/ /
  /   |/ /_ / ____/
 /_/|_/____/_/

====================================================
       KYO QA ServiceNow Knowledge Tool
====================================================
"""
    print(header)

def execute_command(command, description):
    """Executes a command and streams its output for better feedback."""
    logging.info(description)
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in iter(process.stdout.readline, ''):
            print(f"   > {line.strip()}")
        process.wait()
        if process.returncode != 0:
            logging.error(f"Command failed with exit code {process.returncode}")
            return False
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.error(f"Failed to execute command: {e}")
        return False

def setup_environment():
    """Creates a virtual environment and installs dependencies from requirements.txt."""
    python_executable = sys.executable
    
    if not VENV_DIR.exists():
        logging.info("Creating virtual environment...")
        if not execute_command([python_executable, "-m", "venv", str(VENV_DIR)], "✓ Creating venv folder..."):
            return False
        logging.info("Virtual environment created successfully.")
    else:
        logging.info("✓ Virtual environment already exists.")

    python_venv = get_python_executable()
    if not REQUIREMENTS_FILE.exists():
        logging.error(f"FATAL: requirements.txt not found at {REQUIREMENTS_FILE}")
        return False

    logging.info("Verifying and installing dependencies from requirements.txt...")
    command = [str(python_venv), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    if not execute_command(command, "✓ Installing packages..."):
        logging.error("Failed to install dependencies.")
        return False

    logging.info("✅ Environment is ready.")
    return True

def launch_application():
    """Launches the main GUI application using the virtual environment."""
    python_venv = get_python_executable()
    if not MAIN_APP_SCRIPT.exists():
        logging.error(f"FATAL: Main application script not found at {MAIN_APP_SCRIPT}")
        return

    logging.info("\n--- Launching Application ---")
    logging.info("[INFO] A console window will remain open for stability. You can minimize it.")
    try:
        result = subprocess.run(
            [str(python_venv), str(MAIN_APP_SCRIPT)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            logging.info("Application output:\n" + result.stdout)
        if result.stderr:
            logging.error("Application errors:\n" + result.stderr)
        
        if result.returncode != 0:
             logging.error(f"\n--- APPLICATION CRASHED ---")
             logging.error("The application closed unexpectedly. Please review any error messages above.")

    except Exception as e:
        logging.error(f"An unexpected error occurred while launching the application: {e}")

if __name__ == "__main__":
    print_header()
    if setup_environment():
        launch_application()
    else:
        logging.error("\n❌ Setup failed. Please check the logs above for details.")
    
    input("\nPress Enter to exit...")
