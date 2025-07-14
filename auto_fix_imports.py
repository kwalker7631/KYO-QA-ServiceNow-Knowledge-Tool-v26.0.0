# auto_fix_imports.py - Automatically find and fix ALL missing function imports
import ast
import sys
from pathlib import Path
import re

def find_all_missing_imports():
    """Find all missing function imports across all Python files"""
    print("🔍 Scanning for ALL missing function imports...")
    
    python_files = [f for f in Path(".").glob("*.py") 
                   if f.name not in ["auto_fix_imports.py", "find_missing_functions.py"]]
    
    missing_functions = {}
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    module_name = node.module
                    
                    # Only check our internal modules
                    if module_name in ['file_utils', 'config', 'data_harvesters', 'ocr_utils', 
                                     'processing_engine', 'logging_utils', 'custom_exceptions', 
                                     'gui_components', 'kyo_review_tool']:
                        
                        for alias in node.names:
                            function_name = alias.name
                            
                            # Check if function exists
                            if not function_exists(module_name, function_name):
                                if module_name not in missing_functions:
                                    missing_functions[module_name] = set()
                                missing_functions[module_name].add(function_name)
                                
        except Exception as e:
            print(f"  ⚠️  Error parsing {py_file.name}: {e}")
    
    return missing_functions

def function_exists(module_name, function_name):
    """Check if a function exists in a module"""
    try:
        module_file = Path(f"{module_name}.py")
        if not module_file.exists():
            return False
        
        # Try to import and check
        try:
            module = __import__(module_name)
            return hasattr(module, function_name)
        except ImportError:
            # If import fails, check the file content
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for function definition
            pattern = rf"^def\s+{re.escape(function_name)}\s*\("
            return bool(re.search(pattern, content, re.MULTILINE))
            
    except Exception:
        return False

def generate_function_stubs(missing_functions):
    """Generate stub functions for all missing imports"""
    
    function_templates = {
        # File utilities
        'open_file_in_default_app': '''
def open_file_in_default_app(path):
    """Open a file with the default system application."""
    return open_file(path)
''',
        'safe_open_file': '''
def safe_open_file(path):
    """Safely open a file with error handling."""
    return open_file(path)
''',
        'create_directories': '''
def create_directories():
    """Create necessary application directories."""
    return ensure_folders()
''',
        'create_folder_structure': '''
def create_folder_structure():
    """Create application folder structure."""
    return ensure_folders()
''',
        'extract_zip': '''
def extract_zip(zip_path, dest_dir=None):
    """Extract ZIP file to directory."""
    return extract_zip_to_temp(zip_path, dest_dir)
''',
        'unzip_file': '''
def unzip_file(zip_path, dest_dir=None):
    """Unzip a file to directory."""
    return extract_zip_to_temp(zip_path, dest_dir)
''',
        'find_pdf_files': '''
def find_pdf_files(directory, recursive=True):
    """Find PDF files in directory."""
    return find_pdfs_in_directory(directory, recursive)
''',
        'get_pdf_files': '''
def get_pdf_files(directory, recursive=True):
    """Get list of PDF files."""
    return find_pdfs_in_directory(directory, recursive)
''',
        'clean_filename': '''
def clean_filename(filename, max_length=100):
    """Clean filename for safe usage."""
    return get_safe_filename(filename, max_length)
''',
        'sanitize_filename': '''
def sanitize_filename(filename, max_length=100):
    """Sanitize filename for file system."""
    return get_safe_filename(filename, max_length)
''',
        'file_is_locked': '''
def file_is_locked(filepath):
    """Check if file is locked by another process."""
    return is_file_locked(filepath)
''',
        'check_file_lock': '''
def check_file_lock(filepath):
    """Check file lock status."""
    return is_file_locked(filepath)
''',
        
        # GUI Components
        'create_main_header': '''
def create_main_header(parent, version, colors):
    """Create main application header - fallback implementation."""
    try:
        import tkinter as tk
        from tkinter import ttk
        
        header = ttk.Frame(parent, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text=f"KYO QA Tool v{version}", 
                 font=("Arial", 16, "bold")).pack()
        return header
    except Exception as e:
        print(f"Error creating header: {e}")
        return None
''',
        'create_io_section': '''
def create_io_section(parent, app):
    """Create IO section - fallback implementation."""
    try:
        from tkinter import ttk
        frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        frame.pack(fill="x", pady=5)
        return frame
    except Exception as e:
        print(f"Error creating IO section: {e}")
        return None
''',
        'create_process_controls': '''
def create_process_controls(parent, app):
    """Create process controls - fallback implementation."""
    try:
        from tkinter import ttk
        frame = ttk.LabelFrame(parent, text="Controls", padding=10)
        frame.pack(fill="x", pady=5)
        return frame
    except Exception as e:
        print(f"Error creating controls: {e}")
        return None
''',
        'create_status_and_log_section': '''
def create_status_and_log_section(parent, app):
    """Create status section - fallback implementation."""
    try:
        from tkinter import ttk
        frame = ttk.LabelFrame(parent, text="Status", padding=10)
        frame.pack(fill="both", expand=True, pady=5)
        return frame
    except Exception as e:
        print(f"Error creating status section: {e}")
        return None
''',
        
        # Review Tool
        'ReviewWindow': '''
class ReviewWindow:
    """Fallback ReviewWindow class."""
    def __init__(self, parent, pattern_name, pattern_label, file_info=None):
        print(f"ReviewWindow called for {pattern_name} but not fully implemented")
        print("Pattern management is not available")
''',
        
        # Processing Engine
        'run_processing_job': '''
def run_processing_job(job_info, progress_queue, cancel_event, pause_event):
    """Process PDF files - fallback implementation."""
    try:
        progress_queue.put({"type": "log", "tag": "error", 
                           "msg": "Processing engine not fully loaded"})
        progress_queue.put({"type": "finish", "status": "Error"})
    except Exception as e:
        print(f"Processing error: {e}")
''',
        
        # Custom Exceptions
        'FileLockError': '''
class FileLockError(Exception):
    """Exception for file lock errors."""
    pass
''',
        'ExcelGenerationError': '''
class ExcelGenerationError(Exception):
    """Exception for Excel generation errors."""
    pass
''',
        'PDFExtractionError': '''
class PDFExtractionError(Exception):
    """Exception for PDF extraction errors."""
    pass
''',
        'PatternMatchError': '''
class PatternMatchError(Exception):
    """Exception for pattern matching errors."""
    pass
''',
        'ConfigurationError': '''
class ConfigurationError(Exception):
    """Exception for configuration errors."""
    pass
''',
        'KYOQAToolError': '''
class KYOQAToolError(Exception):
    """Base exception for KYO QA Tool errors."""
    pass
''',
        
        # Logging utilities
        'setup_logger': '''
def setup_logger(name, level=None, log_widget=None):
    """Setup logger - basic fallback implementation."""
    import logging
    
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - [%(name)s] - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
''',
        'log_info': '''
def log_info(logger, message):
    """Log info message."""
    logger.info(message)
''',
        'log_error': '''
def log_error(logger, message):
    """Log error message."""
    logger.error(message)
''',
        'log_warning': '''
def log_warning(logger, message):
    """Log warning message."""
    logger.warning(message)
''',
        'create_success_log': '''
def create_success_log(message, output_file=None):
    """Create success log file."""
    if output_file is None:
        from datetime import datetime
        output_file = f"success_{datetime.now():%Y%m%d_%H%M%S}.log"
    
    try:
        with open(output_file, 'w') as f:
            f.write(f"Success: {message}\\n")
        return str(output_file)
    except Exception as e:
        print(f"Error creating success log: {e}")
        return None
''',
        'create_failure_log': '''
def create_failure_log(message, error_details, output_file=None):
    """Create failure log file."""
    if output_file is None:
        from datetime import datetime
        output_file = f"failure_{datetime.now():%Y%m%d_%H%M%S}.log"
    
    try:
        with open(output_file, 'w') as f:
            f.write(f"Failure: {message}\\n")
            f.write(f"Details: {error_details}\\n")
        return str(output_file)
    except Exception as e:
        print(f"Error creating failure log: {e}")
        return None
''',
    }
    
    # Generate patches for each module
    patches = {}
    
    for module_name, functions in missing_functions.items():
        patch_content = f"\n# === AUTO-GENERATED FUNCTIONS FOR {module_name.upper()} ===\n"
        patch_content += f"# Add these functions to {module_name}.py\n\n"
        
        for function_name in sorted(functions):
            if function_name in function_templates:
                patch_content += function_templates[function_name]
            else:
                # Generic stub
                patch_content += f'''
def {function_name}(*args, **kwargs):
    """
    Auto-generated stub for {function_name}.
    TODO: Implement proper functionality.
    """
    print(f"Warning: {function_name} called but not implemented in {module_name}")
    return None
'''
        
        patches[module_name] = patch_content
    
    return patches

def apply_patches(patches):
    """Apply patches to the actual module files"""
    for module_name, patch_content in patches.items():
        module_file = Path(f"{module_name}.py")
        
        if module_file.exists():
            try:
                # Read current content
                with open(module_file, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # Check if already patched
                if "AUTO-GENERATED FUNCTIONS" in current_content:
                    print(f"  ⚠️  {module_name}.py already patched, skipping")
                    continue
                
                # Append patch
                with open(module_file, 'a', encoding='utf-8') as f:
                    f.write(patch_content)
                
                print(f"  ✅ Patched {module_name}.py")
                
            except Exception as e:
                print(f"  ❌ Error patching {module_name}.py: {e}")
        else:
            # Create new file
            try:
                with open(module_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {module_name}.py - Auto-generated module\n")
                    f.write(patch_content)
                
                print(f"  ✅ Created {module_name}.py")
                
            except Exception as e:
                print(f"  ❌ Error creating {module_name}.py: {e}")

def main():
    """Main function"""
    print("KYO QA Tool - Automatic Import Fixer")
    print("=" * 45)
    
    # Find missing functions
    missing = find_all_missing_imports()
    
    if not missing:
        print("✅ No missing function imports found!")
        print("Your application should start successfully.")
        return
    
    print(f"❌ Found missing functions in {len(missing)} modules:")
    for module_name, functions in missing.items():
        print(f"  📦 {module_name}: {len(functions)} missing functions")
        for func in sorted(list(functions)[:5]):  # Show first 5
            print(f"    - {func}")
        if len(functions) > 5:
            print(f"    - ... and {len(functions) - 5} more")
    
    # Generate patches
    print(f"\n🔧 Generating function patches...")
    patches = generate_function_stubs(missing)
    
    # Ask user if they want to apply patches
    response = input(f"\n💡 Apply patches automatically? (y/n): ").lower().strip()
    
    if response == 'y':
        print(f"\n🔧 Applying patches...")
        apply_patches(patches)
        print(f"\n✅ All patches applied!")
        print(f"\n🚀 Try running your application now:")
        print(f"   python launcher.py")
    else:
        # Save patches to files
        print(f"\n💾 Saving patches to files...")
        for module_name, patch_content in patches.items():
            patch_file = f"{module_name}_patch.py"
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write(patch_content)
            print(f"  ✅ Saved {patch_file}")
        
        print(f"\n💡 Manual application:")
        print(f"   Copy the functions from *_patch.py files to the corresponding .py files")

if __name__ == "__main__":
    main()
