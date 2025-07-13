import unittest
from tkinter import TclError

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
        except Exception as e:
            self.fail(f"App failed to launch: {e}")

if __name__ == '__main__':
    unittest.main()
