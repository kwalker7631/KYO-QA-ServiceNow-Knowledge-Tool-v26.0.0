import json
import sys
import types
from pathlib import Path
from tests.openpyxl_stub import ensure_openpyxl_stub

sys.path.append(str(Path(__file__).resolve().parents[1]))

ensure_openpyxl_stub()

import kyo_qa_tool_app  # noqa: E402

class DummyVar:
    def __init__(self, v=""):
        self.value = v
    def set(self, v):
        self.value = v
    def get(self):
        return self.value


def test_manual_export(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    data = {"filename": "file.pdf", "status": "Pass", "models": "A"}
    (cache_dir / "a.json").write_text(json.dumps(data))

    monkeypatch.setattr(kyo_qa_tool_app, "CACHE_DIR", cache_dir, raising=False)

    excel = tmp_path / "template.xlsx"
    excel.write_text("x")

    called = {}
    def fake_export(results, excel_path, progress_queue):
        called["results"] = results
        return Path("out.xlsx")
    monkeypatch.setattr(kyo_qa_tool_app.processing_engine, "export_to_excel", fake_export)
    monkeypatch.setattr(kyo_qa_tool_app.filedialog, "askopenfilename", lambda **k: str(excel))
    monkeypatch.setattr(kyo_qa_tool_app, "open_file_in_default_app", lambda p: None)

    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.spinner_label = types.SimpleNamespace(config=lambda **k: None)
    app.progress_bar = types.SimpleNamespace(start=lambda *a, **k: None, stop=lambda: None)
    app.progress_value = DummyVar(0)
    app.progress_percent_var = DummyVar("0%")
    app.status_current_file = DummyVar()

    kyo_qa_tool_app.KyoQAToolApp.manual_export(app)

    assert called["results"][0]["filename"] == "file.pdf"
    assert app.status_current_file.value.startswith("Export complete")
    assert not app.spinner_running
