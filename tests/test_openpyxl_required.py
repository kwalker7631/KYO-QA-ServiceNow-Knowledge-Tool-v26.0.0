import importlib.util
import sys
from pathlib import Path
import queue
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_export_to_excel_requires_openpyxl():
    sys.modules.pop('processing_engine', None)
    sys.modules['openpyxl'] = None
    spec = importlib.util.spec_from_file_location('processing_engine', ROOT / 'processing_engine.py')
    processing_engine = importlib.util.module_from_spec(spec)
    sys.modules['processing_engine'] = processing_engine
    spec.loader.exec_module(processing_engine)
    with pytest.raises(ImportError):
        processing_engine.export_to_excel([], Path('a.xlsx'), queue.Queue())


