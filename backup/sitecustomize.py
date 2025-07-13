"""Site customizations for test runs."""

import sys
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import openpyxl  # noqa: F401
except Exception:
    try:
        from tests.openpyxl_stub import ensure_openpyxl_stub
    except Exception:

        def ensure_openpyxl_stub():
            return

    ensure_openpyxl_stub()
