import queue
from pathlib import Path
import sys
from types import SimpleNamespace

from tests.openpyxl_stub import ensure_openpyxl_stub

ensure_openpyxl_stub()
sys.modules.setdefault("fitz", SimpleNamespace())
sys.modules.setdefault("pytesseract", SimpleNamespace())
sys.modules.setdefault("cv2", SimpleNamespace())
sys.modules.setdefault("PIL", SimpleNamespace(Image=SimpleNamespace()))
import openpyxl

from processing_engine import export_to_excel


def test_export_to_excel(tmp_path):
    # Create a simple workbook with required headers
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Number", "meta", "author"])
    sheet.append(["123", "", ""])
    template_path = tmp_path / "template.xlsx"
    wb.save(template_path)

    results = [
        {
            "filename": "123.pdf",
            "models": "Model1",
            "author": "John Doe",
            "status": "Pass",
        }
    ]

    output_path = export_to_excel(results, template_path, queue.Queue())

    assert output_path is not None
    assert Path(output_path).exists()

    out_wb = openpyxl.load_workbook(output_path)
    out_sheet = out_wb.active
    assert out_sheet.cell(row=2, column=2).value == "Model1"
    assert out_sheet.cell(row=2, column=3).value == "John Doe"
