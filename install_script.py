# install.py - Automated setup script for KYO QA Tool v26.0.0
import sys
import subprocess
import os
from pathlib import Path
import shutil
import time

def print_header():
    """Print installation header"""
    print("=" * 70)
    print("  KYO QA ServiceNow Knowledge Tool v26.0.0")
    print("  Automated Installation & Setup")
    print("=" * 70)

def check_python_version():
    """Check Python version"""
    print("\n[1/6] Checking Python version...")
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    if version_info >= (3, 9):
        print(f"  ✅ Python {version_str} (compatible)")
        return True
    else:
        print(f"  ❌ Python {version_str} (requires 3.9+)")
        print("  💡 Download Python 3.9+ from: https://www.python.org/downloads/")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n[2/6] Creating directories...")
    
    directories = [
        ('logs', 'Application logs'),
        ('output', 'Excel output files'),
        ('PDF_TXT', 'Text extraction cache'),
        ('PDF_TXT/needs_review', 'Review files'),
        ('.cache', 'Processing cache'),
        ('assets', 'Icons and images (optional)'),
    ]
    
    created = 0
    for dir_path, description in directories:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path:20} - {description}")
            created += 1
        except Exception as e:
            print(f"  ⚠️  {dir_path:20} - Error: {e}")
    
    print(f"  📁 Created {created}/{len(directories)} directories")
    return created > 0

def install_dependencies():
    """Install Python dependencies"""
    print("\n[3/6] Installing dependencies...")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("  ⚠️  requirements.txt not found, installing core packages...")
        core_packages = [
            "pandas>=2.0.0",
            "openpyxl>=3.1.0", 
            "PyMuPDF>=1.23.0",
            "Pillow>=10.0.0",
            "opencv-python>=4.8.0",
            "numpy>=1.24.0",
            "pytesseract>=0.3.10",
            "colorama>=0.4.6"
        ]
        
        for package in core_packages:
            try:
                print(f"  📦 Installing {package}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  ✅ {package.split('>=')[0]}")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {package}")
        
    else:
        try:
            print("  📦 Installing from requirements.txt...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("  ✅ All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install dependencies: {e}")
            print("  💡 Try running manually: pip install -r requirements.txt")
            return False

def check_tesseract():
    """Check Tesseract OCR installation"""
    print("\n[4/6] Checking Tesseract OCR...")
    
    try:
        import pytesseract
        
        # Check for portable version first
        portable_path = Path("tesseract/tesseract.exe")
        if portable_path.exists():
            print("  ✅ Portable Tesseract found")
            pytesseract.pytesseract.tesseract_cmd = str(portable_path)
        
        # Test Tesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract version: {version}")
        return True
        
    except ImportError:
        print("  ⚠️  pytesseract not available (will be limited to text-based PDFs)")
        return False
    except Exception as e:
        print("  ⚠️  Tesseract not found or not working")
        print("  💡 Install from: https://github.com/tesseract-ocr/tesseract")
        if sys.platform.startswith('win'):
            print("     Windows: Download installer from UB Mannheim")
        elif sys.platform.startswith('linux'):
            print("     Linux: sudo apt-get install tesseract-ocr")
        elif sys.platform.startswith('darwin'):
            print("     macOS: brew install tesseract")
        return False

def test_application():
    """Test application startup"""
    print("\n[5/6] Testing application...")
    
    required_files = [
        'kyo_qa_tool_app.py',
        'config.py',
        'version.py',
        'launcher.py'
    ]
    
    missing_files = []
    for filename in required_files:
        if not Path(filename).exists():
            missing_files.append(filename)
    
    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    try:
        # Test imports
        print("  🔄 Testing imports...")
        
        import config
        print("  ✅ Configuration loaded")
        
        import version
        print(f"  ✅ Version: {version.VERSION}")
        
        # Test GUI (without showing window)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("  ✅ GUI framework available")
        
        print("  ✅ Application test passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Application test failed: {e}")
        return False

def create_launcher():
    """Create platform-appropriate launcher"""
    print("\n[6/6] Creating launcher...")
    
    try:
        if sys.platform.startswith('win'):
            # Create/update START.bat
            bat_content = '''@echo off
title KYO QA Tool Launcher v26.0.0
echo Starting KYO QA Tool...
python launcher.py
pause
'''
            with open("START.bat", "w") as f:
                f.write(bat_content)
            print("  ✅ Created START.bat")
        
        else:
            # Create shell script for Unix-like systems
            sh_content = '''#!/bin/bash
echo "Starting KYO QA Tool..."
python3 launcher.py
read -p "Press Enter to continue..."
'''
            with open("start.sh", "w") as f:
                f.write(sh_content)
            os.chmod("start.sh", 0o755)
            print("  ✅ Created start.sh")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create launcher: {e}")
        return False

def print_summary(results):
    """Print installation summary"""
    print("\n" + "=" * 70)
    print("  INSTALLATION SUMMARY")
    print("=" * 70)
    
    total_steps = len(results)
    passed_steps = sum(1 for result in results.values() if result)
    
    print(f"\nSetup Results: {passed_steps}/{total_steps} steps completed")
    
    # Show results
    step_names = {
        'python_version': 'Python Version',
        'directories': 'Directory Creation', 
        'dependencies': 'Dependencies',
        'tesseract': 'Tesseract OCR',
        'application': 'Application Test',
        'launcher': 'Launcher Creation'
    }
    
    for key, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        name = step_names.get(key, key)
        print(f"  {status} - {name}")
    
    # Final recommendations
    print("\n📋 Next Steps:")
    
    if passed_steps == total_steps:
        print("  🎉 Installation completed successfully!")
        print("  🚀 Launch the application:")
        if sys.platform.startswith('win'):
            print("     - Double-click START.bat, or")
        else:
            print("     - Run ./start.sh, or")
        print("     - Run: python launcher.py")
        
    elif passed_steps >= total_steps - 1:
        print("  ⚠️  Installation mostly successful with minor issues")
        print("  🔄 Try launching: python launcher.py")
        print("  🔍 Run diagnostics: python comprehensive_diagnostic.py")
        
    else:
        print("  ❌ Installation had significant issues")
        print("  🔍 Run full diagnostics: python comprehensive_diagnostic.py")
        print("  📖 Check README.md for manual installation steps")
    
    if not results.get('tesseract', True):
        print("\n💡 OCR Note:")
        print("  - Tesseract OCR is optional but recommended")
        print("  - The tool works for text-based PDFs without it")
        print("  - Install Tesseract to process scanned documents")

def main():
    """Main installation function"""
    print_header()
    
    results = {}
    
    try:
        # Run installation steps
        results['python_version'] = check_python_version()
        results['directories'] = create_directories()
        results['dependencies'] = install_dependencies()
        results['tesseract'] = check_tesseract()
        results['application'] = test_application()
        results['launcher'] = create_launcher()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        return
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal installation error: {e}")
    finally:
        input("\nPress Enter to exit...")
