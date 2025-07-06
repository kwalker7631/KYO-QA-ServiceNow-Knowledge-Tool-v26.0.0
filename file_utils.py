# file_utils.py
import os
import sys
import shutil
import tempfile
import logging
import platform
from tkinter import messagebox
from pathlib import Path
import stat # Required for changing file attributes
import zipfile # ADDED for zip extraction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def try_unlock_file(filepath: Path) -> bool:
    """
    Attempts to remove the read-only attribute from a file.
    Returns True if the operation was attempted, False otherwise.
    """
    try:
        # Get current permissions and add write permission for the owner
        current_permissions = os.stat(filepath).st_mode
        os.chmod(filepath, current_permissions | stat.S_IWRITE)
        logging.info(f"Attempted to remove read-only attribute from {filepath.name}")
        return True
    except (OSError, PermissionError) as e:
        logging.warning(f"Could not change file attributes for {filepath.name}: {e}")
        return False

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, works for both development and for PyInstaller.
    """
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path.cwd()
    return base_path / relative_path

def find_tesseract_executable():
    """
    Find the tesseract.exe executable in a prioritized order.
    """
    logging.info("Searching for Tesseract executable...")
    
    search_paths = []
    if getattr(sys, 'frozen', False):
        search_paths.append(Path(sys._MEIPASS) / 'Tesseract-OCR' / 'tesseract.exe')
    
    # Add portable location
    search_paths.append(Path.cwd() / 'tesseract' / 'tesseract.exe')
    
    # Add typical installation locations
    if platform.system() == "Windows":
        search_paths.extend([
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Tesseract-OCR" / "tesseract.exe"
        ])
    else:
        # Unix-like systems typically have tesseract in PATH
        tesseract_paths = shutil.which("tesseract")
        if tesseract_paths:
            search_paths.append(Path(tesseract_paths))
    
    for path in search_paths:
        if path.exists():
            logging.info(f"Found Tesseract at: {path}")
            return str(path)

    error_message = "Tesseract OCR executable not found. Please ensure Tesseract is installed and accessible."
    logging.error(error_message)
    messagebox.showerror("Dependency Error", error_message)
    raise FileNotFoundError(error_message)

def is_file_locked(filepath):
    """
    Checks if a file is locked by attempting to open it in exclusive mode.
    Works on both Windows and Unix-like systems.
    """
    if not Path(filepath).exists():
        logging.warning(f"File does not exist: {filepath}")
        return False
        
    try:
        if platform.system() == "Windows":
            # On Windows, use msvcrt for file locking check
            try:
                import msvcrt
                with open(filepath, 'rb') as f:
                    # Try to get an exclusive lock
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    # If we get here, the file isn't locked
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                return False
            except (IOError, PermissionError):
                return True
        else:
            # On Unix-like systems, use fcntl
            try:
                import fcntl
                with open(filepath, 'a+b') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            except (IOError, PermissionError):
                return True
    except (ImportError, Exception) as e:
        # Fallback method if platform-specific modules are unavailable
        logging.warning(f"Using fallback lock detection for {filepath}: {e}")
        try:
            with open(filepath, 'a+b'):
                pass
            return False
        except (IOError, PermissionError) as e:
            logging.warning(f"File is locked: {filepath}. Reason: {e}")
            return True

def create_temp_working_dir():
    """
    Creates a temporary directory to safely store and process file copies.
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix="kyo_qa_")
        logging.info(f"Created temporary working directory: {temp_dir}")
        return Path(temp_dir)
    except Exception as e:
        logging.error(f"Failed to create temporary directory: {e}")
        messagebox.showerror("Error", f"Could not create a temporary working directory: {e}")
        return None

def extract_zip_to_temp(zip_path: Path) -> Path | None:
    """
    Extracts a zip file to a new temporary directory.
    Returns the Path to the temporary directory, or None on failure.
    """
    temp_dir = create_temp_working_dir()
    if not temp_dir:
        return None
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        logging.info(f"Successfully extracted '{zip_path.name}' to '{temp_dir}'")
        return temp_dir
    except zipfile.BadZipFile:
        logging.error(f"Error: '{zip_path.name}' is not a valid zip file.")
        messagebox.showerror("Invalid File", f"'{zip_path.name}' is not a valid zip file.")
        cleanup_directory(temp_dir)
        return None
    except Exception as e:
        logging.error(f"Failed to extract zip file '{zip_path.name}': {e}")
        messagebox.showerror("Extraction Error", f"Could not extract the zip file:\n{e}")
        cleanup_directory(temp_dir)
        return None

def cleanup_directory(directory_path):
    """
    Recursively deletes the specified directory and all its contents.
    """
    if not directory_path or not os.path.exists(directory_path):
        logging.warning(f"Cleanup skipped: Directory does not exist or path is invalid: {directory_path}")
        return
        
    try:
        shutil.rmtree(directory_path)
        logging.info(f"Successfully cleaned up directory: {directory_path}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during cleanup of {directory_path}: {e}")
        messagebox.showwarning("Cleanup Failed", f"An error occurred while cleaning up files:\n{e}")

def setup_output_folders(base_dir):
    """
    Creates all necessary output subdirectories and returns their Path objects.
    """
    base_path = Path(base_dir)
    try:
        locked_files_dir = base_path / "locked_files"
        needs_review_dir = base_path / "needs_review"
        
        locked_files_dir.mkdir(parents=True, exist_ok=True)
        needs_review_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "locked_files": locked_files_dir,
            "needs_review": needs_review_dir
        }
    except Exception as e:
        logging.error(f"Could not create output subdirectories in {base_dir}: {e}")
        return {}

# --- Compatibility Functions ---
def open_file(filepath):
    """Opens a file with the default application."""
    filepath = Path(filepath)
    if not filepath.exists():
        logging.error(f"Failed to open file - not found: {filepath}")
        messagebox.showerror("Error", f"Could not open the file because it doesn't exist:\n{filepath}")
        return
        
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open '{filepath}'")
        else:  # Linux and other Unix
            os.system(f"xdg-open '{filepath}'")
    except Exception as e:
        logging.error(f"Failed to open file {filepath}: {e}")
        messagebox.showerror("Error", f"Could not open the file:\n{filepath}\n\nError: {e}")

def ensure_folders(base_dir=None):
    """Alias for setup_output_folders for backward compatibility."""
    from config import OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR, NEED_REVIEW_DIR
    
    # Create the base directories
    for directory in [OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create needs_review subdirectory
    review_dir = NEED_REVIEW_DIR / "needs_review"
    review_dir.mkdir(parents=True, exist_ok=True)
    
    return setup_output_folders(base_dir or OUTPUT_DIR)

def cleanup_temp_files(directory_path):
    """Alias for cleanup_directory for backward compatibility."""
    logging.warning("Using deprecated function 'cleanup_temp_files'. Please switch to 'cleanup_directory'.")
    cleanup_directory(directory_path)
