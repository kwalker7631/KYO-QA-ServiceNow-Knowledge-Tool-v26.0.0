import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pkg.kyo_qa_tool_app", ROOT / "kyo_qa_tool_app.py", submodule_search_locations=[str(ROOT)]
)
pkg = types.ModuleType("pkg")
pkg.__path__ = [str(ROOT)]
sys.modules.setdefault("pkg", pkg)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

def test_package_import():
    assert hasattr(module, "KyoQAToolApp")
