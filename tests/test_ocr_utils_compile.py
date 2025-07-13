import py_compile
from pathlib import Path


def test_ocr_utils_py_compile():
    target = Path(__file__).resolve().parents[1] / "ocr_utils.py"
    py_compile.compile(str(target), doraise=True)
