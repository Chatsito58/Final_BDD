import os
import sys
import types
from pathlib import Path
from datetime import datetime

# make project root importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# stub dotenv
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

# ----------------------- stubs for GUI libs -----------------------
class _Widget:
    def __init__(self, *a, **k):
        pass
    def pack(self, *a, **k):
        return self
    def grid(self, *a, **k):
        return self
    def place(self, *a, **k):
        return self
    def configure(self, *a, **k):
        return self
    def destroy(self, *a, **k):
        return self
    def bind(self, *a, **k):
        return self
    def insert(self, *a, **k):
        return self
    def delete(self, *a, **k):
        return self
    def size(self):
        return 0
    def get(self, *a, **k):
        return ""
    def set(self, *a, **k):
        return self
    def winfo_children(self):
        return []
    def after(self, *a, **k):
        if len(a) >= 2 and callable(a[1]):
            a[1]()
    def withdraw(self, *a, **k):
        return self
    def geometry(self, *a, **k):
        return self
    def focus_force(self, *a, **k):
        return self
    def wm_state(self, *a, **k):
        return self
    def __getattr__(self, name):
        def method(*a, **k):
            return self
        return method

class _Var:
    def __init__(self, value=None):
        self._val = value
    def get(self):
        return self._val
    def set(self, val):
        self._val = val
    def trace_add(self, *a, **k):
        pass

class _DateEntry(_Widget):
    def get_date(self):
        return datetime.now().date()

class _Tabview(_Widget):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._tabs = {}
    def add(self, name):
        self._tabs[name] = _Widget()
        return name
    def tab(self, name):
        return self._tabs.get(name, _Widget())

# customtkinter stub
ctk = types.ModuleType('customtkinter')
ctk.CTk = _Widget
ctk.CTkFrame = _Widget
ctk.CTkLabel = _Widget
ctk.CTkEntry = _Widget
ctk.CTkButton = _Widget
ctk.CTkTabview = _Tabview
ctk.CTkTextbox = _Widget
ctk.CTkToplevel = _Widget
ctk.CTkOptionMenu = _Widget
ctk.StringVar = _Var
sys.modules.setdefault('customtkinter', ctk)

# tkinter stub
tk = types.ModuleType('tkinter')
tk.Frame = _Widget
tk.Scrollbar = _Widget
tk.Listbox = _Widget
tk.Text = _Widget
tk.OptionMenu = _Widget
tk.StringVar = _Var
tk.IntVar = _Var
tk.DoubleVar = _Var
tk.Toplevel = _Widget
tk.END = 'end'
class _MB:
    def showinfo(self, *a, **k):
        pass
    def showwarning(self, *a, **k):
        pass
    def showerror(self, *a, **k):
        pass

tk.messagebox = _MB()
tk.ttk = types.SimpleNamespace(Combobox=_Widget, Treeview=_Widget)
tk.Label = _Widget
tk.Entry = _Widget
tk.Spinbox = _Widget
def _getattr(name):
    return _Widget
tk.__getattr__ = lambda name: _getattr(name)
sys.modules.setdefault('tkinter', tk)

# tkcalendar stub
cal = types.ModuleType('tkcalendar')
cal.DateEntry = _DateEntry
sys.modules.setdefault('tkcalendar', cal)

# ------------------------------------------------------------------

from src.sqlite_manager import SQLiteManager
from src.views.ctk_views import (
    ClienteView,
    AdminView,
    GerenteView,
    EmpleadoVentasView,
    EmpleadoCajaView,
    EmpleadoMantenimientoView,
)

class DummyDB:
    def __init__(self, path):
        os.environ['LOCAL_DB_PATH'] = str(path)
        self.sqlite = SQLiteManager()
        self.offline = True
    def execute_query(self, q, params=None, fetch=True, return_lastrowid=False):
        return self.sqlite.execute_query(q, params, fetch, return_lastrowid)

def test_views_instantiation(tmp_path):
    db = DummyDB(tmp_path / 'test.db')
    ctk.CTk().withdraw()
    usuarios = {
        ClienteView: {'usuario': 'cli', 'rol': 'cliente', 'id_cliente': 1},
        AdminView: {'usuario': 'adm', 'rol': 'admin'},
        GerenteView: {'usuario': 'ger', 'rol': 'gerente', 'id_sucursal': 1},
        EmpleadoVentasView: {'usuario': 'ven', 'rol': 'empleado', 'id_sucursal': 1},
        EmpleadoCajaView: {'usuario': 'caj', 'rol': 'empleado', 'id_sucursal': 1},
        EmpleadoMantenimientoView: {'usuario': 'man', 'rol': 'empleado', 'id_sucursal': 1},
    }
    for cls, data in usuarios.items():
        view = cls(data, db)
        view.destroy()


def test_cargar_reservas_cliente(tmp_path, monkeypatch):
    db = DummyDB(tmp_path / 'reservas.db')
    ctk.CTk().withdraw()
    view = ClienteView({'usuario': 'cli', 'rol': 'cliente', 'id_cliente': 1}, db)
    reservas = [
        (
            1,
            datetime(2099, 1, 1, 10, 0),
            datetime(2099, 1, 2, 10, 0),
            'ABC123',
            'Corolla',
            'ABC123',
            100000,
            70000,
            30000,
            'Pendiente',
            'Seguro',
            25000,
            'Desc',
            5000,
            '2024-01-01',
            '2024-12-31',
        )
    ]
    monkeypatch.setattr(db, 'execute_query', lambda *a, **k: reservas)
    view._cargar_reservas_cliente(1)
    view.destroy()
