import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from branding import KyoceraColors


def test_branding_aliases():
    assert KyoceraColors.BACKGROUND_WIDGET == KyoceraColors.WIDGET_BG
    assert KyoceraColors.TEXT_PRIMARY == KyoceraColors.TEXT_DARK
    assert KyoceraColors.TEXT_SECONDARY == KyoceraColors.TEXT_MUTED
    assert KyoceraColors.PRIMARY_BLUE == KyoceraColors.PRIMARY_ACTION
    assert KyoceraColors.STATUS_INFO == KyoceraColors.STATUS_INFO_TEXT


def test_high_contrast_colors():
    assert KyoceraColors.HIGH_CONTRAST_BG == "#000000"
    assert KyoceraColors.HIGH_CONTRAST_TEXT == "#FFFFFF"

