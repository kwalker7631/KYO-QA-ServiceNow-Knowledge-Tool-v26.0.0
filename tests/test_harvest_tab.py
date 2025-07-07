import sys
import types
from pathlib import Path
from tests.openpyxl_stub import ensure_openpyxl_stub

sys.path.append(str(Path(__file__).resolve().parents[1]))

ensure_openpyxl_stub()
sys.modules.setdefault("fitz", types.ModuleType("fitz"))
sys.modules.pop("processing_engine", None)

import kyo_qa_tool_app  # noqa: E402


def test_export_harvest_results(monkeypatch, tmp_path):
    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.harvest_results = [{"filename": "file.pdf", "models": "A", "author": "X"}]
    pdf_path = tmp_path / "file.pdf"
    pdf_path.write_text("dummy")
    app.harvest_file = types.SimpleNamespace(get=lambda: str(pdf_path))
    called = {}

    class DummyExcel:
        def __init__(self, path):
            called["path"] = path
        def create_report(self, data):
            called["data"] = data

    monkeypatch.setattr(kyo_qa_tool_app, "ExcelGenerator", DummyExcel)
    monkeypatch.setattr(kyo_qa_tool_app.messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(kyo_qa_tool_app.messagebox, "showerror", lambda *a, **k: None)
    app.status_current_file = types.SimpleNamespace(set=lambda x: called.setdefault("status", x))
    app.harvest_export_btn = types.SimpleNamespace(config=lambda **kw: None)

    kyo_qa_tool_app.KyoQAToolApp.export_harvest_results(app)

    assert called["data"] == app.harvest_results
    assert pdf_path.with_name("file_harvest.xlsx").as_posix() == called["path"]
    assert "Export complete" in called["status"]
