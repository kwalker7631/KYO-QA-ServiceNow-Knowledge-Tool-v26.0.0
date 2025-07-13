import unittest
from utils import apply_recycles

class ApplyRecyclesTest(unittest.TestCase):
    def test_apply_recycles_default(self):
        text = "This  is   spaced"
        self.assertEqual(apply_recycles(text), "This is spaced")

if __name__ == '__main__':
    unittest.main()
