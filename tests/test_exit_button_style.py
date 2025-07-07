import os
import sys
import types
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import pytest

if not os.environ.get("DISPLAY"):
    pytest.skip("Tk display not available", allow_module_level=True)

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui_components
from branding import KyoceraColors


def test_setup_high_contrast_creates_exit_style():
    root = tk.Tk()
    root.withdraw()
    gui_components.setup_high_contrast_styles(root)
    style = ttk.Style(root)
    bg = style.lookup("Exit.TButton", "background")
    fg = style.lookup("Exit.TButton", "foreground")
    root.destroy()
    assert bg == KyoceraColors.HIGH_CONTRAST_BG
    assert fg == KyoceraColors.HIGH_CONTRAST_TEXT


def test_create_footer_uses_exit_style(monkeypatch):
    root = tk.Tk()
    root.withdraw()
    dummy_app = types.SimpleNamespace(
        fullscreen_status_var=tk.StringVar(),
        on_closing=lambda: None,
    )
    created = {}
    orig_button = ttk.Button

    def spy_button(master, **kw):
        created["style"] = kw.get("style")
        return orig_button(master, **kw)

    monkeypatch.setattr(ttk, "Button", spy_button)
    gui_components.create_footer(root, dummy_app)
    root.destroy()
    assert created.get("style") == "Exit.TButton"
