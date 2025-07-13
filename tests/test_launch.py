import unittest
try:
    import tkinter
    from tkinter import TclError
except Exception:  # pragma: no cover - tkinter not installed
    tkinter = None
    TclError = Exception

from kyo_qa_tool_app import KyoQAToolApp

class LaunchTest(unittest.TestCase):
    def test_app_launch(self):
        if tkinter is None:
            self.skipTest("Tkinter not available")
        try:
            app = KyoQAToolApp()
            app.withdraw()
            app.update()
            app.destroy()
        except TclError:
            self.skipTest("Tkinter display not available")
        except Exception as e:
            self.fail(f"App failed to launch: {e}")

if __name__ == "__main__":
    unittest.main()
