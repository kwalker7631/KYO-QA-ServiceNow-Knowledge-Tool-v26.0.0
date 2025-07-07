import queue
from pathlib import Path

from tests.openpyxl_stub import ensure_openpyxl_stub

ensure_openpyxl_stub()

import processing_engine  # noqa: E402


class DummyCell:
    def __init__(self, value=None):
        self.value = value


class DummySheet:
    def __init__(self):
        self.rows = {
            1: [DummyCell("Number"), DummyCell(processing_engine.META_COLUMN_NAME), DummyCell(processing_engine.AUTHOR_COLUMN_NAME)],
            2: [DummyCell("file1"), DummyCell(None), DummyCell(None)],
        }

    def __getitem__(self, idx):
        return self.rows[idx]

    def iter_cols(self, min_col, max_col, min_row):
        for row in range(min_row, max(self.rows) + 1):
            yield self.rows[row][min_col - 1]

    def cell(self, row, column):
        return self.rows.setdefault(row, [DummyCell(None) for _ in range(3)])[column - 1]


class DummyWorkbook:
    def __init__(self):
        self.active = DummySheet()
        self.saved_path = None

    def save(self, path):
        self.saved_path = Path(path)


def test_export_to_excel_creates_file_and_logs_success(tmp_path, monkeypatch):
    excel = tmp_path / "base.xlsx"
    excel.write_text("x")
    wb = DummyWorkbook()
    monkeypatch.setattr(processing_engine.openpyxl, "load_workbook", lambda *_: wb)
    monkeypatch.setattr(processing_engine.time, "strftime", lambda *_: "20220101-000000")
    q = queue.Queue()
    results = [{"filename": "file1.pdf", "status": "Pass", "models": "meta", "author": "me"}]

    output = processing_engine.export_to_excel(results, excel, q)

    assert wb.saved_path == output
    assert output.parent == tmp_path
    msg = q.get_nowait()
    assert msg["type"] == "log" and msg["tag"] == "success"
