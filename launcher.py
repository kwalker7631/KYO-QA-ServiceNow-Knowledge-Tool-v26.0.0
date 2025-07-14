# launcher.py - Simple and reliable launcher for KYO QA Tool
import sys
import subprocess
import traceback
from pathlib import Path

def print_header():
    """Print application header"""
    print("=" * 60)
    print("  KYO QA ServiceNow Knowledge Tool v26.0.0")
    print("  Simple Launcher")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    min_version = (3, 9)
    current_version = sys.version_info[:2]
    
    print(f"Python version: {sys.version.split()[0]}")
    
    if current_version < min_version:
        print(f"❌ ERROR: Python {'.'.join(map(str, min_version))}+ required")
        print(f"   You have Python {'.'.join(map(str, current_version))}")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_critical_dependencies():
    """Check if critical dependencies are available"""
    critical_deps = [
        ('tkinter', 'GUI framework'),
        ('pandas', 'Data processing'),
        ('openpyxl', 'Excel handling')
    ]
    
    print("\nChecking critical dependencies...")
    missing = []
    
    for package, description in critical_deps:
        try:
            if package == 'tkinter':
                import tkinter
                # Test if we can create a window
                root = tkinter.Tk()
                root.withdraw()
                root.destroy()
            else:
                __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - MISSING: {description}")
            missing.append(package)
        except Exception as e:
            print(f"⚠️  {package} - ERROR: {e}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install pandas openpyxl")
        if 'tkinter' in missing:
            print("💡 For tkinter on Linux: sudo apt-get install python3-tk")
        return False
    
    print("✅ All critical dependencies available")
    return True

def check_application_files():
    """Check if main application files exist"""
    required_files = [
        'kyo_qa_tool_app.py',
        'config.py',
        'version.py'
    ]
    
    print("\nChecking application files...")
    missing = []
    
    for filename in required_files:
        if Path(filename).exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - MISSING")
            missing.append(filename)
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        print("💡 Ensure all application files are in the same directory")
        return False
    
    print("✅ All required files present")
    return True

def create_necessary_folders():
    """Create necessary application folders"""
    try:
        folders = ['logs', 'output', 'PDF_TXT', 'assets']
        
        print("\nCreating necessary folders...")
        for folder in folders:
            Path(folder).mkdir(exist_ok=True)
            print(f"✅ {folder}/ folder ready")
        
        # Create subdirectories
        (Path('PDF_TXT') / 'needs_review').mkdir(exist_ok=True)
        
        return True
    except Exception as e:
        print(f"⚠️  Error creating folders: {e}")
        return True  # Non-critical error

def launch_application():
    """Launch the main application"""
    try:
        print("\n🚀 Starting KYO QA Tool...")
        print("   (You can minimize this console window)")
        
        # Import and run the main application
        from kyo_qa_tool_app import KyoQAToolApp
        
        app = KyoQAToolApp()
        app.mainloop()
        
        print("\n✅ Application closed normally")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("💡 Make sure all Python files are in the same directory")
        print("💡 Check that all dependencies are installed")
        
    except Exception as e:
        print(f"\n❌ Application Error: {e}")
        print("\nFull error details:")
        traceback.print_exc()

def main():
    """Main launcher function"""
    try:
        print_header()
        
        # Run all checks
        checks_passed = True
        
        if not check_python_version():
            checks_passed = False
        
        if not check_critical_dependencies():
            checks_passed = False
        
        if not check_application_files():
            checks_passed = False
        
        # Create folders (non-critical)
        create_necessary_folders()
        
        if not checks_passed:
            print("\n❌ Some checks failed. Please fix the issues above.")
            print("\nTroubleshooting:")
            print("1. Install missing dependencies: pip install -r requirements.txt")
            print("2. Ensure all application files are present")
            print("3. Check Python version is 3.9 or higher")
        else:
            print("\n✅ All checks passed!")
            launch_application()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        traceback.print_exc()
    
    finally:
        print("\n" + "=" * 60)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
