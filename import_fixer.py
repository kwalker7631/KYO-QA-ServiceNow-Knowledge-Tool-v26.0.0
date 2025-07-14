# aggressive_import_fixer.py - Parse actual import errors and fix them automatically
import re
import subprocess
import sys
from pathlib import Path

def run_app_and_capture_errors():
    """Run the application and capture import errors"""
    print("🔍 Running application to capture import errors...")
    
    try:
        # Run the launcher and capture output
        result = subprocess.run([
            sys.executable, "launcher.py"
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout + result.stderr
        return output
        
    except subprocess.TimeoutExpired:
        print("⚠️  Application took too long to respond")
        return ""
    except Exception as e:
        print(f"⚠️  Error running application: {e}")
        return ""

def extract_missing_imports(output):
    """Extract missing import information from error output"""
    missing_imports = []
    
    # Pattern to match import errors
    import_error_pattern = r"cannot import name '([^']+)' from '([^']+)'"
    
    matches = re.findall(import_error_pattern, output)
    
    for function_name, module_name in matches:
        missing_imports.append({
            'function': function_name,
            'module': module_name
        })
        print(f"📋 Found missing: {function_name} from {module_name}")
    
    return missing_imports

def generate_function_stub(function_name, module_name):
    """Generate a function stub based on the function name"""
    
    # GUI component functions
    if 'section' in function_name.lower():
        if 'status' in function_name.lower():
            return f'''
def {function_name}(parent, app):
    """Auto-generated alias for status section."""
    return create_status_and_log_section(parent, app)
'''
        elif 'control' in function_name.lower() or 'button' in function_name.lower():
            return f'''
def {function_name}(parent, app):
    """Auto-generated alias for controls section."""
    return create_process_controls(parent, app)
'''
        elif 'input' in function_name.lower() or 'file' in function_name.lower() or 'io' in function_name.lower():
            return f'''
def {function_name}(parent, app):
    """Auto-generated alias for input/output section."""
    return create_io_section(parent, app)
'''
        elif 'header' in function_name.lower() or 'title' in function_name.lower():
            return f'''
def {function_name}(parent, version, colors=None):
    """Auto-generated alias for header section."""
    return create_main_header(parent, version, colors)
'''
        else:
            # Generic section function
            return f'''
def {function_name}(parent, app):
    """Auto-generated section function."""
    try:
        frame = ttk.LabelFrame(parent, text="{function_name.replace('_', ' ').title()}", padding=10)
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text="Section placeholder").pack()
        return frame
    except Exception as e:
        print(f"Error in {function_name}: {{e}}")
        return None
'''
    
    # Layout and setup functions
    elif 'setup' in function_name.lower() or 'create_main' in function_name.lower():
        return f'''
def {function_name}(*args, **kwargs):
    """Auto-generated setup function."""
    try:
        print("Setup function {function_name} called")
        return True
    except Exception as e:
        print(f"Error in {function_name}: {{e}}")
        return False
'''
    
    # Processing functions
    elif module_name == 'processing_engine':
        return f'''
def {function_name}(*args, **kwargs):
    """Auto-generated processing function."""
    try:
        print("Processing function {function_name} called but not fully implemented")
        if len(args) > 0 and hasattr(args[0], 'put'):
            # Looks like a queue, send error message
            args[0].put({{"type": "log", "tag": "error", "msg": "Function {function_name} not implemented"}})
            args[0].put({{"type": "finish", "status": "Error"}})
        return None
    except Exception as e:
        print(f"Error in {function_name}: {{e}}")
        return None
'''
    
    # File utility functions
    elif module_name == 'file_utils':
        if 'open' in function_name.lower():
            return f'''
def {function_name}(path):
    """Auto-generated file opening function."""
    return open_file(path)
'''
        elif 'clean' in function_name.lower() or 'clear' in function_name.lower():
            return f'''
def {function_name}(*args, **kwargs):
    """Auto-generated cleanup function."""
    return cleanup_temp_files()
'''
        else:
            return f'''
def {function_name}(*args, **kwargs):
    """Auto-generated file utility function."""
    print(f"File utility function {function_name} called but not implemented")
    return None
'''
    
    # Exception classes
    elif function_name.endswith('Error') or function_name.endswith('Exception'):
        return f'''
class {function_name}(Exception):
    """Auto-generated exception class."""
    pass
'''
    
    # Generic function
    else:
        return f'''
def {function_name}(*args, **kwargs):
    """Auto-generated function for {function_name}."""
    print(f"Function {function_name} called but not fully implemented")
    return None
'''

def add_missing_functions(missing_imports):
    """Add missing functions to their respective modules"""
    
    modules_to_patch = {}
    
    # Group by module
    for import_info in missing_imports:
        module_name = import_info['module']
        function_name = import_info['function']
        
        if module_name not in modules_to_patch:
            modules_to_patch[module_name] = []
        
        modules_to_patch[module_name].append(function_name)
    
    # Patch each module
    for module_name, functions in modules_to_patch.items():
        module_file = Path(f"{module_name}.py")
        
        if not module_file.exists():
            print(f"⚠️  Module file {module_file} doesn't exist, skipping")
            continue
        
        try:
            # Read current content
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate stubs for missing functions
            stub_content = f"\n\n# === AUTO-GENERATED MISSING FUNCTIONS ===\n"
            
            for function_name in functions:
                # Check if function already exists
                if f"def {function_name}(" in content or f"class {function_name}(" in content:
                    print(f"  ✓ {function_name} already exists in {module_name}")
                    continue
                
                stub = generate_function_stub(function_name, module_name)
                stub_content += stub
                print(f"  + Adding {function_name} to {module_name}")
            
            # Only append if we have new functions to add
            if "# === AUTO-GENERATED MISSING FUNCTIONS ===" not in content and len([f for f in functions if f"def {f}(" not in content]) > 0:
                # Add import statements if needed
                if module_name == 'gui_components':
                    if "import tkinter as tk" not in content:
                        stub_content = "import tkinter as tk\nfrom tkinter import ttk\n" + stub_content
                
                # Append to file
                with open(module_file, 'a', encoding='utf-8') as f:
                    f.write(stub_content)
                
                print(f"  ✅ Patched {module_name}.py")
            else:
                print(f"  ✓ {module_name}.py already patched or no new functions needed")
                
        except Exception as e:
            print(f"  ❌ Error patching {module_name}.py: {e}")

def main():
    """Main function"""
    print("Aggressive Import Fixer")
    print("=" * 40)
    print("This will run your app, capture import errors, and fix them automatically")
    
    # Capture errors from running the app
    output = run_app_and_capture_errors()
    
    if not output:
        print("❌ Could not capture application output")
        return
    
    # Extract missing imports
    missing_imports = extract_missing_imports(output)
    
    if not missing_imports:
        print("✅ No import errors found in output!")
        print("Your application might be working now, or errors are different.")
        return
    
    print(f"\n🔧 Found {len(missing_imports)} missing imports")
    
    # Add missing functions
    add_missing_functions(missing_imports)
    
    print(f"\n✅ Patching complete!")
    print(f"\n🚀 Try running your application again:")
    print(f"   python launcher.py")
    
    # Optionally run again to check
    print(f"\n🔄 Run again to check for more errors? (y/n): ", end="")
    if input().lower().strip() == 'y':
        print("\n" + "="*40)
        main()

if __name__ == "__main__":
    main()
