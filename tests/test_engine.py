import queue
from pathlib import Path
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
            "qa_numbers": "QA-001",
            "author": "John Doe",
            "status": "Pass",
        }
    ]

    output_path = export_to_excel(results, template_path, queue.Queue())

    assert output_path is not None
    assert Path(output_path).exists()

    out_wb = openpyxl.load_workbook(output_path)
    out_sheet = out_wb.active
    assert out_sheet.cell(row=2, column=2).value == "Model1; QA-001"
    assert out_sheet.cell(row=2, column=3).value == "John Doe"


def test_export_with_qa_column(tmp_path):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Number", "meta", "author", "QA Numbers"])
    sheet.append(["123", "", "", ""])
    template_path = tmp_path / "template2.xlsx"
    wb.save(template_path)

    results = [
        {
            "filename": "123.pdf",
            "models": "Model1",
            "qa_numbers": "QA-002",
            "author": "Jane Doe",
            "status": "Pass",
        }
    ]

    output_path = export_to_excel(
        results, template_path, queue.Queue(), qa_column_name="QA Numbers"
    )

    out_wb = openpyxl.load_workbook(output_path)
    out_sheet = out_wb.active
    assert out_sheet.cell(row=2, column=2).value == "Model1"
    assert out_sheet.cell(row=2, column=3).value == "Jane Doe"
    assert out_sheet.cell(row=2, column=4).value == "QA-002"
