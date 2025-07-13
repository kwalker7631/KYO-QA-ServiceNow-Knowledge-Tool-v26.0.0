import queue
from pathlib import Path
import sys
from types import SimpleNamespace
from openpyxl_stub import ensure_openpyxl_stub

ensure_openpyxl_stub()
import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

dummy = SimpleNamespace()
for mod in [
    "fitz",
    "pytesseract",
    "cv2",
    "anthropic",
    "sentry_sdk",
    "sentry_sdk.integrations.logging",
    "extract.common",
    "custom_recycles",
]:
    sys.modules.setdefault(mod, dummy)
sys.modules.setdefault("PIL", SimpleNamespace(Image=SimpleNamespace()))

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

def test_export_to_excel_multiple_rows(tmp_path):
    """Ensure multiple rows are mapped correctly."""
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Number", "meta", "author"])
    sheet.append(["123", "", ""])
    sheet.append(["456", "", ""])
    template_path = tmp_path / "template.xlsx"
    wb.save(template_path)

    results = [
        {
            "filename": "123.pdf",
            "models": "Model1",
            "author": "John Doe",
            "status": "Pass",
        },
        {
            "filename": "456.pdf",
            "models": "Model2",
            "author": "Jane Roe",
            "status": "Pass",
        },
    ]

    output_path = export_to_excel(results, template_path, queue.Queue())

    out_wb = openpyxl.load_workbook(output_path)
    out_sheet = out_wb.active
    assert out_sheet.cell(row=2, column=2).value == "Model1"
    assert out_sheet.cell(row=3, column=2).value == "Model2"

