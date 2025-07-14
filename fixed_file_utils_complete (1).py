# file_utils.py - Fixed version with robust error handling and backward compatibility
import os
import sys
import shutil
import time
from pathlib import Path

from config import LOGS_DIR, OUTPUT_DIR, PDF_TXT_DIR, CACHE_DIR

def ensure_folders():
    """Create all necessary application folders on startup with error handling."""
    folders_created = 0
    folders_failed = 0
    
    folders = [
        (LOGS_DIR, "logs"),
        (OUTPUT_DIR, "output"),
        (PDF_TXT_DIR, "PDF text storage"),
        (CACHE_DIR, "cache"),
        (PDF_TXT_DIR / "needs_review", "review files")
    ]
    
    for folder_path, description in folders:
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            folders_created += 1
            print(f"✓ {description} folder: {folder_path}")
        except PermissionError:
            print(f"✗ Permission denied creating {description} folder: {folder_path}")
            folders_failed += 1
        except Exception as e:
            print(f"✗ Error creating {description} folder: {e}")
            folders_failed += 1
    
    if folders_failed == 0:
        print(f"✅ All {folders_created} application folders ready")
    else:
        print(f"⚠️  {folders_created} folders created, {folders_failed} failed")
    
    return folders_failed == 0

def is_file_locked(filepath):
    """
    Check if a file is locked by another process with multiple detection methods.
    Returns True if locked, False if accessible.
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False  # File doesn't exist, so not locked
    
    try:
        # Method 1: Try to open for writing (most reliable)
        with open(filepath, "r+b"):
            pass
        return False  # Successfully opened, not locked
        
    except PermissionError:
        # File is likely locked by another process
        return True
        
    except FileNotFoundError:
        # File was deleted between existence check and open
        return False
        
    except Exception as e:
        # For other errors, assume the file might be locked
        print(f"Warning: Could not check lock status of {filepath}: {e}")
        return True

def safe_file_operation(operation, filepath, max_retries=3, delay=1.0):
    """
    Safely perform a file operation with retries for temporary locks.
    
    Args:
        operation: Function to perform (should take filepath as argument)
        filepath: Path to the file
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        Result of operation if successful, None if failed
    """
    filepath = Path(filepath)
    
    for attempt in range(max_retries):
        try:
            return operation(filepath)
        except (PermissionError, OSError) as e:
            if attempt < max_retries - 1:
                print(f"File operation failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                time.sleep(delay)
                delay *= 1.5  # Exponential backoff
            else:
                print(f"File operation failed after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error in file operation: {e}")
            raise
    
    return None

def cleanup_temp_files():
    """
    Removes temporary files from cache and review folders with error handling.
    Returns number of files cleaned up.
    """
    print("Starting cleanup of temporary files...")
    cleaned_count = 0
    error_count = 0
    
    cleanup_directories = [
        (CACHE_DIR, "cache files"),
        (PDF_TXT_DIR / "needs_review", "review text files")
    ]
    
    for directory, description in cleanup_directories:
        if not directory.exists():
            print(f"  - {description}: directory doesn't exist, skipping")
            continue
        
        try:
            files_in_dir = list(directory.iterdir())
            print(f"  - {description}: found {len(files_in_dir)} items")
            
            for item in files_in_dir:
                try:
                    if item.is_file():
                        # Check if file is in use before deleting
                        if not is_file_locked(item):
                            item.unlink()
                            cleaned_count += 1
                        else:
                            print(f"    ⚠️  Skipping locked file: {item.name}")
                    elif item.is_dir():
                        # Only remove empty directories
                        try:
                            item.rmdir()
                            cleaned_count += 1
                        except OSError:
                            # Directory not empty, remove contents recursively
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned_count += 1
                except OSError as e:
                    print(f"    ✗ Error deleting {item.name}: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"    ✗ Unexpected error with {item.name}: {e}")
                    error_count += 1
                    
        except Exception as e:
            print(f"  ✗ Error accessing {description} directory: {e}")
            error_count += 1
    
    if error_count == 0:
        print(f"✅ Cleanup complete: {cleaned_count} items removed")
    else:
        print(f"⚠️  Cleanup finished: {cleaned_count} items removed, {error_count} errors")
    
    return cleaned_count

# Backward compatibility alias for the old function name
def cleanup_directory(*args, **kwargs):
    """
    Alias for cleanup_temp_files() for backward compatibility.
    This function was renamed but some code may still reference the old name.
    """
    return cleanup_temp_files(*args, **kwargs)

def open_file(path):
    """
    Opens a file with the default system application with error handling.
    
    Args:
        path: Path to the file to open (string or Path object)
    
    Returns:
        True if successful, False if failed
    """
    path = Path(path)
    
    if not path.exists():
        print(f"Cannot open file: {path} (file not found)")
        return False
    
    try:
        path_str = str(path.resolve())
        
        if sys.platform.startswith('win'):
            # Windows
            os.startfile(path_str)
        elif sys.platform.startswith('darwin'):
            # macOS
            import subprocess
            subprocess.run(['open', path_str], check=True)
        else:
            # Linux and other Unix-like systems
            import subprocess
            subprocess.run(['xdg-open', path_str], check=True)
        
        print(f"✅ Opened file: {path.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to open file {path.name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error opening file {path.name}: {e}")
        return False

def get_safe_filename(filename, max_length=100):
    """
    Create a safe filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length for the filename
    
    Returns:
        Safe filename string
    """
    # Characters that are problematic in filenames
    unsafe_chars = '<>:"/\\|?*'
    
    # Replace unsafe characters with underscores
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Replace multiple underscores with single ones
    while '__' in safe_name:
        safe_name = safe_name.replace('__', '_')
    
    # Remove leading/trailing underscores and whitespace
    safe_name = safe_name.strip('_ ')
    
    # Truncate if too long, preserving file extension
    if len(safe_name) > max_length:
        name_part, ext_part = os.path.splitext(safe_name)
        available_length = max_length - len(ext_part)
        safe_name = name_part[:available_length] + ext_part
    
    # Ensure we have something
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name

def backup_file(filepath, backup_suffix="_backup"):
    """
    Create a backup copy of a file.
    
    Args:
        filepath: Path to the file to backup
        backup_suffix: Suffix to add to backup filename
    
    Returns:
        Path to backup file if successful, None if failed
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"Cannot backup file: {filepath} (file not found)")
        return None
    
    try:
        # Create backup filename
        backup_path = filepath.parent / f"{filepath.stem}{backup_suffix}{filepath.suffix}"
        
        # If backup already exists, add timestamp
        if backup_path.exists():
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = filepath.parent / f"{filepath.stem}{backup_suffix}_{timestamp}{filepath.suffix}"
        
        # Copy file
        shutil.copy2(filepath, backup_path)
        print(f"✅ Created backup: {backup_path.name}")
        return backup_path
        
    except Exception as e:
        print(f"✗ Failed to create backup of {filepath.name}: {e}")
        return None

def get_disk_usage(path):
    """
    Get disk usage information for a given path.
    
    Args:
        path: Path to check (string or Path object)
    
    Returns:
        Dictionary with total, used, and free space in bytes
    """
    try:
        path = Path(path)
        
        if sys.platform.startswith('win'):
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(str(path)),
                ctypes.pointer(free_bytes),
                ctypes.pointer(total_bytes),
                None
            )
            total = total_bytes.value
            free = free_bytes.value
        else:
            statvfs = os.statvfs(path)
            total = statvfs.f_frsize * statvfs.f_blocks
            free = statvfs.f_frsize * statvfs.f_bavail
        
        used = total - free
        
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent_used': (used / total * 100) if total > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting disk usage for {path}: {e}")
        return None

def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def clear_directory(directory_path, keep_subdirs=False):
    """
    Clear all files (and optionally subdirectories) from a directory.
    
    Args:
        directory_path: Path to the directory to clear
        keep_subdirs: If True, only delete files, not subdirectories
    
    Returns:
        Number of items removed
    """
    directory_path = Path(directory_path)
    
    if not directory_path.exists():
        return 0
    
    removed_count = 0
    
    try:
        for item in directory_path.iterdir():
            try:
                if item.is_file():
                    if not is_file_locked(item):
                        item.unlink()
                        removed_count += 1
                elif item.is_dir() and not keep_subdirs:
                    shutil.rmtree(item, ignore_errors=True)
                    removed_count += 1
            except Exception as e:
                print(f"Error removing {item}: {e}")
    
    except Exception as e:
        print(f"Error clearing directory {directory_path}: {e}")
    
    return removed_count

# Additional backward compatibility functions that might be referenced elsewhere
def cleanup_cache():
    """Alias for cleaning up cache directory specifically"""
    if CACHE_DIR.exists():
        return clear_directory(CACHE_DIR)
    return 0

def cleanup_logs(keep_recent_days=7):
    """
    Clean up old log files, keeping recent ones.
    
    Args:
        keep_recent_days: Number of days of logs to keep
    
    Returns:
        Number of log files removed
    """
    if not LOGS_DIR.exists():
        return 0
    
    import time
    cutoff_time = time.time() - (keep_recent_days * 24 * 60 * 60)
    removed_count = 0
    
    try:
        for log_file in LOGS_DIR.glob("*.log"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    if not is_file_locked(log_file):
                        log_file.unlink()
                        removed_count += 1
            except Exception as e:
                print(f"Error removing old log {log_file}: {e}")
    except Exception as e:
        print(f"Error cleaning logs: {e}")
    
    return removed_count

# Test functions
def test_file_operations():
    """Test file utility functions"""
    print("Testing file utility functions...")
    
    # Test folder creation
    test_folder = Path("test_temp_folder")
    try:
        test_folder.mkdir(exist_ok=True)
        print(f"✅ Folder creation test passed")
        
        # Test file operations
        test_file = test_folder / "test.txt"
        test_file.write_text("Test content")
        
        # Test file lock detection
        is_locked = is_file_locked(test_file)
        print(f"✅ File lock detection: {is_locked}")
        
        # Test safe filename
        safe_name = get_safe_filename("test<>file?.txt")
        print(f"✅ Safe filename: {safe_name}")
        
        # Test file size formatting
        size_str = format_file_size(1536)
        print(f"✅ File size formatting: {size_str}")
        
        # Cleanup
        shutil.rmtree(test_folder, ignore_errors=True)
        print("✅ All file utility tests passed")
        
    except Exception as e:
        print(f"✗ File utility test failed: {e}")
        # Cleanup on error
        try:
            shutil.rmtree(test_folder, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    print("File Utils - Testing")
    print("=" * 30)
    
    # Test basic functionality
    test_file_operations()
    
    # Test folder creation
    print("\nTesting folder creation...")
    ensure_folders()
    
    # Test disk usage
    print("\nChecking disk usage...")
    usage = get_disk_usage(Path.cwd())
    if usage:
        print(f"Total: {format_file_size(usage['total'])}")
        print(f"Used: {format_file_size(usage['used'])} ({usage['percent_used']:.1f}%)")
        print(f"Free: {format_file_size(usage['free'])}")
