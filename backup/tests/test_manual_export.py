import json
import queue
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
import importlib.util
import types

dummy = SimpleNamespace()
sys.modules.setdefault("openpyxl", SimpleNamespace(load_workbook=lambda *a, **k: None))
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

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pkg.kyo_qa_tool_app", ROOT / "kyo_qa_tool_app.py", submodule_search_locations=[str(ROOT)]
)
pkg = types.ModuleType("pkg")
pkg.__path__ = [str(ROOT)]
sys.modules.setdefault("pkg", pkg)
app_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app_module
spec.loader.exec_module(app_module)


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


def build_app(tmp_dir, excel_path):
    app = app_module.KyoQAToolApp.__new__(app_module.KyoQAToolApp)
    app.selected_excel = DummyVar(str(excel_path))
    app.response_queue = queue.Queue()
    return app


def test_manual_export_success(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr(app_module, "CACHE_DIR", cache_dir)

    data = {"filename": "a.pdf", "models": "M1", "status": "Pass"}
    with open(cache_dir / "a.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

    excel = tmp_path / "template.xlsx"
    excel.touch()
    app = build_app(cache_dir, excel)

    called = {}

    def fake_export(results, excel_path, progress_queue):
        called["args"] = (results, excel_path, progress_queue)
        return Path("output.xlsx")

    sys.modules["processing_engine"] = SimpleNamespace(export_to_excel=fake_export)

    infos = []
    monkeypatch.setattr(
        app_module.messagebox, "showinfo", lambda t, m: infos.append((t, m))
    )

    app.manual_export()

    assert called["args"][0] == [data]
    assert infos


def test_manual_export_failure(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr(app_module, "CACHE_DIR", cache_dir)

    data = {"filename": "a.pdf", "models": "M1", "status": "Pass"}
    with open(cache_dir / "a.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

    excel = tmp_path / "template.xlsx"
    excel.touch()
    app = build_app(cache_dir, excel)

    def fake_export(results, excel_path, progress_queue):
        return None

    sys.modules["processing_engine"] = SimpleNamespace(export_to_excel=fake_export)

    errors = []
    monkeypatch.setattr(
        app_module.messagebox, "showerror", lambda t, m: errors.append((t, m))
    )

    app.manual_export()

    assert errors
