import unittest
import tkinter
TclError = tkinter.TclError
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kyo_qa_tool_app import KyoQAToolApp


class LaunchTest(unittest.TestCase):
    def test_app_launch(self):
        try:
            app = KyoQAToolApp()
            app.withdraw()
            app.update()
            app.destroy()
        except TclError:
            self.skipTest("Tkinter display not available")
        except Exception as exc:
            self.fail(f"App failed to launch: {exc}")


if __name__ == "__main__":
    unittest.main()
