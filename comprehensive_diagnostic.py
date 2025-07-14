# comprehensive_diagnostic.py - Complete diagnostic for KYO QA Tool v26.0.0
import sys
import traceback
import importlib
import subprocess
import platform
from pathlib import Path
from datetime import datetime

class DiagnosticTester:
    def __init__(self):
        self.results = {}
        self.critical_failures = []
        self.warnings = []
        self.recommendations = []
    
    def print_header(self):
        """Print diagnostic header"""
        print("=" * 80)
        print("  KYO QA ServiceNow Knowledge Tool v26.0.0")
        print("  Comprehensive System Diagnostic")
        print("=" * 80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print("=" * 80)
    
    def test_python_environment(self):
        """Test Python version and basic environment"""
        print("\n[1/10] Testing Python Environment...")
        
        try:
            version_info = sys.version_info
            version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
            
            if version_info >= (3, 9):
                print(f"  ✅ Python {version_str} (compatible)")
                self.results['python_version'] = True
            else:
                print(f"  ❌ Python {version_str} (requires 3.9+)")
                self.results['python_version'] = False
                self.critical_failures.append("Python version too old")
            
            # Test basic modules
            basic_modules = ['os', 'sys', 'pathlib', 'datetime', 'json', 'threading']
            for module in basic_modules:
                try:
                    __import__(module)
                    print(f"  ✅ {module}")
                except ImportError:
                    print(f"  ❌ {module} (missing)")
                    self.critical_failures.append(f"Basic module {module} missing")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Python environment test failed: {e}")
            self.critical_failures.append("Python environment test failed")
            return False
    
    def test_critical_dependencies(self):
        """Test critical Python packages"""
        print("\n[2/10] Testing Critical Dependencies...")
        
        critical_deps = {
            'tkinter': 'GUI framework (built-in)',
            'pandas': 'Data manipulation',
            'openpyxl': 'Excel file handling',
        }
        
        all_critical_ok = True
        
        for package, description in critical_deps.items():
            try:
                if package == 'tkinter':
                    import tkinter as tk
                    # Test if we can create a window
                    root = tk.Tk()
                    root.withdraw()
                    root.destroy()
                else:
                    importlib.import_module(package)
                
                print(f"  ✅ {package:15} - {description}")
                
            except ImportError:
                print(f"  ❌ {package:15} - MISSING: {description}")
                self.critical_failures.append(f"Critical dependency missing: {package}")
                all_critical_ok = False
            except Exception as e:
                print(f"  ⚠️  {package:15} - ERROR: {e}")
                self.warnings.append(f"Issue with {package}: {e}")
        
        self.results['critical_dependencies'] = all_critical_ok
        return all_critical_ok
    
    def test_optional_dependencies(self):
        """Test optional but important packages"""
        print("\n[3/10] Testing Optional Dependencies...")
        
        optional_deps = {
            'fitz': 'PDF processing (PyMuPDF)',
            'PIL': 'Image processing (Pillow)',
            'cv2': 'Computer vision (opencv-python)',
            'pytesseract': 'OCR functionality',
            'numpy': 'Numerical operations',
            'colorama': 'Colored terminal output',
        }
        
        available_count = 0
        total_count = len(optional_deps)
        
        for package, description in optional_deps.items():
            try:
                importlib.import_module(package)
                print(f"  ✅ {package:15} - {description}")
                available_count += 1
            except ImportError:
                print(f"  ⚠️  {package:15} - MISSING: {description}")
                self.warnings.append(f"Optional dependency missing: {package}")
        
        print(f"\n  📊 Optional packages: {available_count}/{total_count} available")
        
        if available_count < total_count * 0.7:  # Less than 70%
            self.warnings.append("Many optional dependencies are missing")
        
        self.results['optional_dependencies'] = available_count / total_count
        return available_count > 0
    
    def test_application_files(self):
        """Test if all required application files exist"""
        print("\n[4/10] Testing Application Files...")
        
        required_files = [
            ('kyo_qa_tool_app.py', 'Main application'),
            ('config.py', 'Configuration'),
            ('version.py', 'Version information'),
            ('processing_engine.py', 'Processing logic'),
            ('data_harvesters.py', 'Data extraction'),
            ('ocr_utils.py', 'OCR utilities'),
            ('file_utils.py', 'File operations'),
            ('logging_utils.py', 'Logging system'),
        ]
        
        missing_files = []
        
        for filename, description in required_files:
            file_path = Path(filename)
            if file_path.exists():
                # Check if file is readable and not empty
                try:
                    size = file_path.stat().st_size
                    if size > 0:
                        print(f"  ✅ {filename:25} - {description} ({size:,} bytes)")
                    else:
                        print(f"  ⚠️  {filename:25} - Empty file")
                        self.warnings.append(f"File {filename} is empty")
                except Exception as e:
                    print(f"  ⚠️  {filename:25} - Cannot read: {e}")
                    self.warnings.append(f"Cannot read {filename}: {e}")
            else:
                print(f"  ❌ {filename:25} - MISSING: {description}")
                missing_files.append(filename)
        
        # Check optional files
        optional_files = [
            'gui_components.py',
            'kyo_review_tool.py',
            'custom_patterns.py',
            'requirements.txt',
            'README.md'
        ]
        
        print("\n  Optional files:")
        for filename in optional_files:
            if Path(filename).exists():
                print(f"  ✅ {filename}")
            else:
                print(f"  ⚠️  {filename} - missing (optional)")
        
        if missing_files:
            self.critical_failures.extend([f"Missing file: {f}" for f in missing_files])
        
        self.results['application_files'] = len(missing_files) == 0
        return len(missing_files) == 0
    
    def test_directory_structure(self):
        """Test directory structure and permissions"""
        print("\n[5/10] Testing Directory Structure...")
        
        required_dirs = [
            ('logs', 'Log files'),
            ('output', 'Excel output'),
            ('PDF_TXT', 'Text extraction'),
            ('.cache', 'Processing cache'),
        ]
        
        optional_dirs = [
            ('assets', 'Icons and images'),
            ('tests', 'Unit tests'),
            ('docs', 'Documentation'),
        ]
        
        dir_issues = []
        
        for dirname, description in required_dirs:
            dir_path = Path(dirname)
            
            if dir_path.exists():
                if dir_path.is_dir():
                    # Test write permissions
                    try:
                        test_file = dir_path / "test_write.tmp"
                        test_file.write_text("test")
                        test_file.unlink()
                        print(f"  ✅ {dirname:15} - {description} (writable)")
                    except PermissionError:
                        print(f"  ⚠️  {dirname:15} - No write permission")
                        self.warnings.append(f"No write permission for {dirname}")
                    except Exception as e:
                        print(f"  ⚠️  {dirname:15} - Write test failed: {e}")
                        self.warnings.append(f"Write test failed for {dirname}: {e}")
                else:
                    print(f"  ❌ {dirname:15} - Exists but not a directory")
                    dir_issues.append(dirname)
            else:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ {dirname:15} - Created successfully")
                except Exception as e:
                    print(f"  ❌ {dirname:15} - Cannot create: {e}")
                    dir_issues.append(dirname)
        
        print("\n  Optional directories:")
        for dirname, description in optional_dirs:
            dir_path = Path(dirname)
            if dir_path.exists():
                print(f"  ✅ {dirname:15} - {description}")
            else:
                print(f"  ⚠️  {dirname:15} - Missing (optional)")
        
        if dir_issues:
            self.critical_failures.extend([f"Directory issue: {d}" for d in dir_issues])
        
        self.results['directory_structure'] = len(dir_issues) == 0
        return len(dir_issues) == 0
    
    def test_tesseract_ocr(self):
        """Test Tesseract OCR availability"""
        print("\n[6/10] Testing Tesseract OCR...")
        
        try:
            import pytesseract
            
            # Test portable Tesseract
            portable_path = Path("tesseract") / "tesseract.exe"
            if portable_path.exists():
                print(f"  ✅ Portable Tesseract found: {portable_path}")
                pytesseract.pytesseract.tesseract_cmd = str(portable_path)
            
            # Test Tesseract functionality
            try:
                version = pytesseract.get_tesseract_version()
                print(f"  ✅ Tesseract version: {version}")
                
                # Test OCR on a simple image
                from PIL import Image
                import numpy as np
                
                # Create a simple test image with text
                img_array = np.ones((100, 200, 3), dtype=np.uint8) * 255
                test_img = Image.fromarray(img_array)
                
                try:
                    text = pytesseract.image_to_string(test_img)
                    print(f"  ✅ OCR test completed")
                    self.results['tesseract_ocr'] = True
                    return True
                except Exception as e:
                    print(f"  ⚠️  OCR test failed: {e}")
                    self.warnings.append(f"OCR test failed: {e}")
                    self.results['tesseract_ocr'] = False
                    return False
                
            except Exception as e:
                print(f"  ❌ Tesseract not working: {e}")
                self.warnings.append("Tesseract installed but not working")
                self.results['tesseract_ocr'] = False
                return False
                
        except ImportError:
            print("  ❌ pytesseract not installed")
            print("  💡 Install with: pip install pytesseract")
            print("  💡 Also install Tesseract: https://github.com/tesseract-ocr/tesseract")
            self.warnings.append("OCR functionality not available")
            self.results['tesseract_ocr'] = False
            return False
    
    def test_configuration(self):
        """Test application configuration"""
        print("\n[7/10] Testing Configuration...")
        
        try:
            import config
            
            # Test required configuration attributes
            required_attrs = [
                'BRAND_COLORS', 'MODEL_PATTERNS', 'OUTPUT_DIR', 
                'LOGS_DIR', 'PDF_TXT_DIR', 'CACHE_DIR'
            ]
            
            missing_attrs = []
            for attr in required_attrs:
                if hasattr(config, attr):
                    print(f"  ✅ {attr}")
                else:
                    print(f"  ❌ {attr} - missing")
                    missing_attrs.append(attr)
            
            # Test pattern validity
            if hasattr(config, 'MODEL_PATTERNS'):
                import re
                invalid_patterns = []
                for i, pattern in enumerate(config.MODEL_PATTERNS):
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        invalid_patterns.append((i, pattern, str(e)))
                
                if invalid_patterns:
                    print(f"  ⚠️  {len(invalid_patterns)} invalid regex patterns")
                    self.warnings.append(f"Invalid regex patterns found")
                else:
                    print(f"  ✅ All {len(config.MODEL_PATTERNS)} regex patterns valid")
            
            if missing_attrs:
                self.critical_failures.extend([f"Missing config: {attr}" for attr in missing_attrs])
            
            self.results['configuration'] = len(missing_attrs) == 0
            return len(missing_attrs) == 0
            
        except ImportError as e:
            print(f"  ❌ Cannot import config: {e}")
            self.critical_failures.append("Cannot import configuration")
            self.results['configuration'] = False
            return False
        except Exception as e:
            print(f"  ❌ Configuration error: {e}")
            self.critical_failures.append(f"Configuration error: {e}")
            self.results['configuration'] = False
            return False
    
    def test_gui_basic(self):
        """Test basic GUI functionality"""
        print("\n[8/10] Testing GUI Functionality...")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Test basic window creation
            root = tk.Tk()
            root.title("Test Window")
            root.withdraw()  # Hide the window
            
            # Test ttk styles
            style = ttk.Style()
            themes = style.theme_names()
            print(f"  ✅ Available themes: {', '.join(themes)}")
            
            # Test widget creation
            frame = ttk.Frame(root)
            label = ttk.Label(frame, text="Test")
            button = ttk.Button(frame, text="Test")
            entry = ttk.Entry(frame)
            
            print(f"  ✅ Basic widgets created successfully")
            
            root.destroy()
            
            self.results['gui_basic'] = True
            return True
            
        except ImportError as e:
            print(f"  ❌ GUI import error: {e}")
            if sys.platform.startswith('linux'):
                print("  💡 On Linux, install with: sudo apt-get install python3-tk")
            self.critical_failures.append("GUI not available")
            self.results['gui_basic'] = False
            return False
        except Exception as e:
            print(f"  ❌ GUI test failed: {e}")
            self.warnings.append(f"GUI test failed: {e}")
            self.results['gui_basic'] = False
            return False
    
    def test_main_application_import(self):
        """Test importing the main application"""
        print("\n[9/10] Testing Main Application Import...")
        
        try:
            # Try to import main application modules
            modules_to_test = [
                ('kyo_qa_tool_app', 'Main application'),
                ('processing_engine', 'Processing engine'),
                ('data_harvesters', 'Data harvesters'),
                ('ocr_utils', 'OCR utilities'),
            ]
            
            import_failures = []
            
            for module_name, description in modules_to_test:
                try:
                    module = importlib.import_module(module_name)
                    print(f"  ✅ {module_name:20} - {description}")
                except ImportError as e:
                    print(f"  ❌ {module_name:20} - Import failed: {e}")
                    import_failures.append(module_name)
                except Exception as e:
                    print(f"  ⚠️  {module_name:20} - Error: {e}")
                    self.warnings.append(f"Import warning for {module_name}: {e}")
            
            if import_failures:
                self.critical_failures.extend([f"Import failed: {m}" for m in import_failures])
            
            self.results['main_application_import'] = len(import_failures) == 0
            return len(import_failures) == 0
            
        except Exception as e:
            print(f"  ❌ Application import test failed: {e}")
            self.critical_failures.append("Application import test failed")
            self.results['main_application_import'] = False
            return False
    
    def test_application_instantiation(self):
        """Test creating the main application instance"""
        print("\n[10/10] Testing Application Instantiation...")
        
        try:
            # Import the main application class
            from kyo_qa_tool_app import KyoQAToolApp
            
            print("  ✅ Main application class imported")
            
            # Try to create an instance (but don't run mainloop)
            print("  🔄 Creating application instance...")
            app = KyoQAToolApp()
            print("  ✅ Application instance created successfully")
            
            # Test basic functionality
            if hasattr(app, 'log_message'):
                app.log_message("Test message", "info")
                print("  ✅ Logging functionality works")
            
            # Clean up
            try:
                app.destroy()
                print("  ✅ Application cleanup successful")
            except:
                pass  # Ignore cleanup errors
            
            self.results['application_instantiation'] = True
            return True
            
        except Exception as e:
            print(f"  ❌ Application instantiation failed: {e}")
            print("\n  Detailed error:")
            traceback.print_exc()
            self.critical_failures.append("Cannot create application instance")
            self.results['application_instantiation'] = False
            return False
    
    def generate_report(self):
        """Generate final diagnostic report"""
        print("\n" + "=" * 80)
        print("  DIAGNOSTIC REPORT")
        print("=" * 80)
        
        # Count results
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result is True)
        failed_tests = total_tests - passed_tests
        
        print(f"\nTest Results: {passed_tests}/{total_tests} passed")
        
        # Show test results
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            formatted_name = test_name.replace('_', ' ').title()
            print(f"  {status} - {formatted_name}")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n❌ Critical Issues ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"  • {failure}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  • ... and {len(self.warnings) - 5} more warnings")
        
        # Recommendations
        self._generate_recommendations()
        if self.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in self.recommendations:
                print(f"  • {rec}")
        
        # Overall status
        if not self.critical_failures:
            print(f"\n🎉 Overall Status: READY TO RUN")
            print("   Your application should start successfully!")
        elif len(self.critical_failures) <= 2:
            print(f"\n⚠️  Overall Status: NEEDS MINOR FIXES")
            print("   Fix the critical issues above and try again.")
        else:
            print(f"\n❌ Overall Status: NEEDS MAJOR FIXES") 
            print("   Multiple critical issues need to be resolved.")
        
        print("\n" + "=" * 80)
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        
        if not self.results.get('critical_dependencies'):
            self.recommendations.append("Install missing dependencies: pip install pandas openpyxl")
            if sys.platform.startswith('linux'):
                self.recommendations.append("Install tkinter: sudo apt-get install python3-tk")
        
        if not self.results.get('tesseract_ocr'):
            self.recommendations.append("Install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")
        
        if self.results.get('optional_dependencies', 1) < 0.7:
            self.recommendations.append("Install all dependencies: pip install -r requirements.txt")
        
        if not self.results.get('application_files'):
            self.recommendations.append("Ensure all Python files are in the same directory")
        
        if not self.results.get('directory_structure'):
            self.recommendations.append("Check file/folder permissions in the application directory")
        
        if not self.results.get('gui_basic'):
            self.recommendations.append("Fix GUI/display issues before running the application")
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        self.print_header()
        
        try:
            # Run all tests
            self.test_python_environment()
            self.test_critical_dependencies()
            self.test_optional_dependencies()
            self.test_application_files()
            self.test_directory_structure()
            self.test_tesseract_ocr()
            self.test_configuration()
            self.test_gui_basic()
            self.test_main_application_import()
            self.test_application_instantiation()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Diagnostic interrupted by user")
        except Exception as e:
            print(f"\n❌ Diagnostic failed with error: {e}")
            traceback.print_exc()
        
        finally:
            self.generate_report()

def main():
    """Main function to run diagnostics"""
    try:
        tester = DiagnosticTester()
        tester.run_all_tests()
    except Exception as e:
        print(f"Fatal error running diagnostics: {e}")
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
