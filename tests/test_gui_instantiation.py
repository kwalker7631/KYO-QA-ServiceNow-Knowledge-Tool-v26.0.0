import sys
import types
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from openpyxl_stub import ensure_openpyxl_stub

ensure_openpyxl_stub()

class DummyTk(types.ModuleType):
    class Tk:
        def __init__(self, *a, **k):
            self.children = {}

        def title(self, *a, **k):
            pass

        def geometry(self, *a, **k):
            pass

        def minsize(self, *a, **k):
            pass

        def protocol(self, *a, **k):
            pass

        def bind(self, *a, **k):
            pass

        def destroy(self, *a, **k):
            pass

        def after(self, *a, **k):
            pass

    class Toplevel:
        pass

    class StringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value):
            self.value = value

        def get(self):
            return self.value

    IntVar = StringVar
    DoubleVar = StringVar
    HORIZONTAL = 0

sys.modules["tkinter"] = DummyTk("tkinter")
ttk_stub = types.ModuleType("tkinter.ttk")
ttk_stub.Style = lambda *a, **k: types.SimpleNamespace(
    configure=lambda *a, **k: None,
    map=lambda *a, **k: None,
    theme_use=lambda *a, **k: None,
)
class _Widget:
    def pack(self, *a, **k):
        pass

    def grid(self, *a, **k):
        pass

    def configure(self, *a, **k):
        pass

    def columnconfigure(self, *a, **k):
        pass

    def rowconfigure(self, *a, **k):
        pass

    def add(self, *a, **k):
        return _Widget()

def stub_widget(*a, **k):
    return _Widget()
ttk_stub.Frame = stub_widget
ttk_stub.Notebook = stub_widget
ttk_stub.Label = stub_widget
ttk_stub.LabelFrame = stub_widget
ttk_stub.Button = stub_widget
ttk_stub.Entry = stub_widget
ttk_stub.Combobox = stub_widget
ttk_stub.Scrollbar = stub_widget
ttk_stub.Treeview = stub_widget
ttk_stub.Progressbar = stub_widget
ttk_stub.PanedWindow = stub_widget
sys.modules["tkinter.ttk"] = ttk_stub
filedialog_stub = types.ModuleType("tkinter.filedialog")
filedialog_stub.askdirectory = lambda *a, **k: ""
filedialog_stub.askopenfilename = lambda *a, **k: ""
filedialog_stub.askopenfilenames = lambda *a, **k: []
sys.modules["tkinter.filedialog"] = filedialog_stub
messagebox_stub = types.ModuleType("tkinter.messagebox")
messagebox_stub.showwarning = lambda *a, **k: None
messagebox_stub.showerror = lambda *a, **k: None
messagebox_stub.askyesno = lambda *a, **k: False
messagebox_stub.showinfo = lambda *a, **k: None
sys.modules["tkinter.messagebox"] = messagebox_stub
spec = importlib.util.spec_from_file_location("app", ROOT / "kyo_qa_tool_app.py")
app_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app_module
spec.loader.exec_module(app_module)


def test_app_instantiation():
    app_module.KyoQAToolApp._setup_window = lambda self: None
    app_module.KyoQAToolApp._create_widgets = lambda self: None
    app_module.KyoQAToolApp()
