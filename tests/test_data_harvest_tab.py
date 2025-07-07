import types
from types import SimpleNamespace
import gui_components


def test_create_data_harvest_tab_styles(monkeypatch):
    configs = {}

    class DummyStyle:
        def __init__(self, app=None):
            pass

        def configure(self, name, **kwargs):
            configs[name] = kwargs

        def theme_use(self, *args, **kwargs):
            pass

        def map(self, *args, **kwargs):
            pass

    dummy_widget = SimpleNamespace(pack=lambda *a, **k: None, grid=lambda *a, **k: None)

    monkeypatch.setattr(gui_components.ttk, "Style", DummyStyle)
    monkeypatch.setattr(gui_components.ttk, "Frame", lambda *a, **k: dummy_widget)
    monkeypatch.setattr(gui_components.ttk, "Label", lambda *a, **k: dummy_widget)
    monkeypatch.setattr(gui_components.ttk, "Button", lambda *a, **k: dummy_widget)
    monkeypatch.setattr(gui_components.tk, "Text", lambda *a, **k: dummy_widget)

    gui_components.create_data_harvest_tab(None, SimpleNamespace())

    assert (
        configs["Harvest.TFrame"]["background"]
        == gui_components.KyoceraColors.HIGH_CONTRAST_BG
    )
    assert (
        configs["Harvest.TLabel"]["foreground"]
        == gui_components.KyoceraColors.HIGH_CONTRAST_TEXT
    )
