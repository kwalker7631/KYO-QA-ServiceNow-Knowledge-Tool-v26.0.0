import sys
import json
import types
from pathlib import Path
from tests.openpyxl_stub import ensure_openpyxl_stub

sys.path.append(str(Path(__file__).resolve().parents[1]))

ensure_openpyxl_stub()
sys.modules.setdefault("fitz", types.ModuleType("fitz"))
sys.modules.setdefault("cv2", types.ModuleType("cv2"))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))

import kyo_qa_tool_app  # noqa: E402


class DummyTree:
    def __init__(self):
        self.rows = []

    def delete(self, *args):
        self.rows.clear()

    def get_children(self):
        return list(range(len(self.rows)))

    def insert(self, parent, index, values=()):
        self.rows.append({"values": values, "tags": ()})
        return len(self.rows) - 1

    def item(self, iid, **kw):
        if "tags" in kw:
            self.rows[iid]["tags"] = kw["tags"]
        return self.rows[iid]

    def tag_configure(self, *args, **kwargs):
        pass


def test_load_review_data(monkeypatch, tmp_path):
    cache_dir = tmp_path
    data1 = {"filename": "file1.pdf", "status": "Pass"}
    data2 = {"filename": "file2.pdf", "status": "Needs Review"}
    (cache_dir / "a.json").write_text(json.dumps(data1))
    (cache_dir / "b.json").write_text(json.dumps(data2))

    monkeypatch.setattr(kyo_qa_tool_app, "CACHE_DIR", cache_dir, raising=False)

    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.review_filter = types.SimpleNamespace(get=lambda: "All")
    tree = DummyTree()
    app.review_table = tree
    app.spinner_label = types.SimpleNamespace(config=lambda **k: None)
    app.progress_bar = types.SimpleNamespace(start=lambda *a, **k: None, stop=lambda: None)
    class DummyVar:
        def __init__(self, v=0):
            self.value = v
        def set(self, v):
            self.value = v
        def get(self):
            return self.value
    app.progress_value = DummyVar()
    app.progress_percent_var = DummyVar()
    app.status_current_file = DummyVar("")

    kyo_qa_tool_app.KyoQAToolApp.load_review_data(app)

    assert len(tree.rows) == 2
    filenames = {row["values"][0] for row in tree.rows}
    assert {"file1.pdf", "file2.pdf"} == filenames
    assert app.status_current_file.value == "Review loaded 2 items."
    assert not app.spinner_running
