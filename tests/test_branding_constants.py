import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from branding import KyoceraColors


EXPECTED_COLORS = {
    "KYOCERA_RED": "#DA291C",
    "BACKGROUND_MAIN": "#F0F2F5",
    "WIDGET_BG": "#FFFFFF",
    "TEXT_DARK": "#212529",
    "TEXT_MUTED": "#6c757d",
    "HIGH_CONTRAST_BG": "#000000",
    "HIGH_CONTRAST_TEXT": "#FFFFFF",
    "PRIMARY_ACTION": "#0d6efd",
    "PRIMARY_ACTION_HOVER": "#0b5ed7",
    "BORDER_COLOR": "#ced4da",
    "STATUS_SUCCESS": "#198754",
    "STATUS_WARNING": "#ffc107",
    "STATUS_ERROR": "#dc3545",
    "STATUS_INFO_TEXT": "#0dcaf0",
}


def test_branding_constants():
    for attr, expected in EXPECTED_COLORS.items():
        assert getattr(KyoceraColors, attr) == expected
