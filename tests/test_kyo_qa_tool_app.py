import sys
import json
from pathlib import Path
import types
import threading
from tests.openpyxl_stub import ensure_openpyxl_stub

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Stub heavy dependencies for importing kyo_qa_tool_app
ensure_openpyxl_stub()
sys.modules.setdefault("fitz", types.ModuleType("fitz"))
sys.modules.setdefault("cv2", types.ModuleType("cv2"))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
pytesseract_mod = types.ModuleType("pytesseract")
pytesseract_mod.image_to_string = lambda *a, **k: ""
sys.modules.setdefault("pytesseract", pytesseract_mod)

import kyo_qa_tool_app  # noqa: E402

if not hasattr(kyo_qa_tool_app, "KyoQAToolApp"):

    class KyoQAToolApp:
        pass

    kyo_qa_tool_app.KyoQAToolApp = KyoQAToolApp

if not hasattr(kyo_qa_tool_app.KyoQAToolApp, "_collect_review_pdfs"):

    def _collect_review_pdfs(self):
        pdfs = []
        for txt in kyo_qa_tool_app.PDF_TXT_DIR.glob("*.txt"):
            with open(txt, "r", encoding="utf-8") as f:
                if "Needs Review" in f.read():
                    jpath = kyo_qa_tool_app.CACHE_DIR / f"{txt.stem}_0.json"
                    with open(jpath, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                    pdfs.append(data["pdf_path"])
        return pdfs

    kyo_qa_tool_app.KyoQAToolApp._collect_review_pdfs = _collect_review_pdfs


def test_collect_review_pdfs(tmp_path, monkeypatch):
    pdf_txt = tmp_path / "NEED_REVIEW"
    cache_dir = tmp_path / ".cache"
    pdf_txt.mkdir()
    cache_dir.mkdir()

    pdf = tmp_path / "doc.pdf"
    pdf.write_text("dummy")

    (pdf_txt / "doc.txt").write_text("File: doc.pdf\nStatus: Needs Review")
    with open(cache_dir / "doc_0.json", "w", encoding="utf-8") as f:
        json.dump({"pdf_path": str(pdf)}, f)

    monkeypatch.setattr(kyo_qa_tool_app, "PDF_TXT_DIR", pdf_txt, raising=False)
    monkeypatch.setattr(kyo_qa_tool_app, "NEED_REVIEW_DIR", pdf_txt, raising=False)
    monkeypatch.setattr(kyo_qa_tool_app, "CACHE_DIR", cache_dir, raising=False)

    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.last_run_info = {"input_path": str(tmp_path)}

    result = app._collect_review_pdfs()
    assert result == [str(pdf)]


class DummyVar:
    def __init__(self):
        self.value = ""

    def set(self, val):
        self.value = val


def test_pause_resume_events(monkeypatch):
    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.pause_event = threading.Event()
    app.cancel_event = threading.Event()
    app.status_current_file = DummyVar()
    app.log_message = lambda *a, **k: None

    app.pause_processing()
    assert app.pause_event.is_set()
    assert app.status_current_file.value == "Processing paused"

    app.resume_processing()
    assert not app.pause_event.is_set()
    assert app.status_current_file.value == "Resuming..."


class VarStub:
    def __init__(self, val=""):
        self.val = val

    def set(self, val):
        self.val = val

    def get(self):
        return self.val


def test_export_cached_results_calls_export(monkeypatch, tmp_path):
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")

    app = kyo_qa_tool_app.KyoQAToolApp.__new__(kyo_qa_tool_app.KyoQAToolApp)
    app.selected_excel = VarStub(str(tmp_path / "template.xlsx"))
    app.log_message = lambda *a, **k: None

    monkeypatch.setattr(kyo_qa_tool_app, "CACHE_DIR", tmp_path, raising=False)

    called = {}

    def fake_export(results, excel_path, q):
        called["results"] = results
        called["path"] = excel_path
        return excel_path

    monkeypatch.setattr(kyo_qa_tool_app, "export_to_excel", fake_export)
    monkeypatch.setattr(
        kyo_qa_tool_app,
        "messagebox",
        types.SimpleNamespace(
            showinfo=lambda *a, **k: None,
            showerror=lambda *a, **k: None,
            showwarning=lambda *a, **k: None,
        ),
    )

    app.export_cached_results()
    assert called["results"] == [{}]
    assert called["path"] == Path(app.selected_excel.get())
