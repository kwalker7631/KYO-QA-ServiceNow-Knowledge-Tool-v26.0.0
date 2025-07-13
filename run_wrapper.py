
import sys
import importlib

try:
    import kyo_qa_tool_app
    kyo_qa_tool_app.main()
except ImportError as e:
    module_name = str(e).split("'")[-2] if "'" in str(e) else str(e).split()[-1]
    if module_name:
        print(f"\nMissing dependency: {module_name}")
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
            print("\nPlease run the following command manually:")
            print(f"  {sys.executable} -m pip install {module_name}")
            input("\nPress Enter to exit...")
    else:
        print(f"\nImport error: {e}")
        input("\nPress Enter to exit...")
except Exception as e:
    print(f"\nApplication error: {e}")
    input("\nPress Enter to exit...")
