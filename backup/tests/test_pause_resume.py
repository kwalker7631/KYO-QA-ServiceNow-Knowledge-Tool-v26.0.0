import sys
import types
import threading
import unittest
from types import SimpleNamespace
from pathlib import Path

# Stub heavy dependencies before importing the app module
for name in [
    "openpyxl",
    "PIL",
    "PIL.Image",
    "PyMuPDF",
    "fitz",
    "pytesseract",
    "cv2",
    "Pillow",
]:
    sys.modules.setdefault(name, types.ModuleType(name))


class DummyTk(types.ModuleType):
    class Tk:
        def __init__(self, *a, **k):
            pass

    class Toplevel:
        pass

    class StringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value):
            self.value = value

        def get(self):
            return self.value

    IntVar = StringVar


sys.modules.setdefault("tkinter", DummyTk("tkinter"))
sys.modules.setdefault("tkinter.ttk", types.ModuleType("tkinter.ttk"))
sys.modules.setdefault("tkinter.filedialog", types.ModuleType("tkinter.filedialog"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import importlib.util
import types

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pkg.kyo_qa_tool_app", ROOT / "kyo_qa_tool_app.py", submodule_search_locations=[str(ROOT)]
)
pkg = types.ModuleType("pkg")
pkg.__path__ = [str(ROOT)]
sys.modules.setdefault("pkg", pkg)
app_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app_module
spec.loader.exec_module(app_module)
KyoQAToolApp = app_module.KyoQAToolApp


class DummyVar:
    def __init__(self):
        self.value = ""

    def set(self, value):
        self.value = value


class PauseResumeTest(unittest.TestCase):
    def test_pause_and_resume(self):
        dummy = SimpleNamespace(
            pause_event=threading.Event(), status_current_file=DummyVar()
        )
        KyoQAToolApp.pause_processing(dummy)
        self.assertTrue(dummy.pause_event.is_set())
        self.assertEqual(dummy.status_current_file.value, "Processing paused")
        KyoQAToolApp.resume_processing(dummy)
        self.assertFalse(dummy.pause_event.is_set())
        self.assertEqual(dummy.status_current_file.value, "Resuming...")

    def test_idempotent_calls(self):
        dummy = SimpleNamespace(
            pause_event=threading.Event(), status_current_file=DummyVar()
        )
        KyoQAToolApp.pause_processing(dummy)
        initial_status = dummy.status_current_file.value
        KyoQAToolApp.pause_processing(dummy)
        self.assertTrue(dummy.pause_event.is_set())
        self.assertEqual(dummy.status_current_file.value, initial_status)

        KyoQAToolApp.resume_processing(dummy)
        initial_status = dummy.status_current_file.value
        KyoQAToolApp.resume_processing(dummy)
        self.assertFalse(dummy.pause_event.is_set())
        self.assertEqual(dummy.status_current_file.value, initial_status)


if __name__ == "__main__":
    unittest.main()
