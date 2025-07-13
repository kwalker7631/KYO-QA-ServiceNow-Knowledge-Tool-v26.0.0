import importlib.util
import sys
from pathlib import Path
import queue
import pytest

ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture
def temporary_sys_path():
    original_sys_path = sys.path[:]
    sys.path.insert(0, str(ROOT))
    yield
    sys.path = original_sys_path


def test_export_to_excel_requires_openpyxl(temporary_sys_path):
    sys.modules.pop('processing_engine', None)
    sys.modules.pop('openpyxl', None)
    spec = importlib.util.spec_from_file_location('processing_engine', ROOT / 'processing_engine.py')
    processing_engine = importlib.util.module_from_spec(spec)
    sys.modules['processing_engine'] = processing_engine
    spec.loader.exec_module(processing_engine)
    with pytest.raises(ImportError):
        processing_engine.export_to_excel([], Path('a.xlsx'), queue.Queue())


