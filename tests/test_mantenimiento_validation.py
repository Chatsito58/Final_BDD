import pytest

try:  # Skip if GUI libs missing
    import customtkinter  # noqa: F401
except Exception:  # pragma: no cover - dependency missing
    pytest.skip("GUI libraries not installed", allow_module_level=True)

from src.views import ctk_views


class DummyDB:
    def __init__(self, state=1):
        self.state = state
        self.queries = []
        self.offline = False

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        self.queries.append(query)
        if "SELECT id_estado_vehiculo" in query:
            return [(self.state,)]
        return []


def make_dummy_listbox(placa):
    class L:
        def curselection(self):
            return (0,)

        def get(self, idx):
            return f"{placa} | model"

    return L()


def test_marcar_revisado_checks_vehicle_state(monkeypatch):
    db = DummyDB(state=2)
    view = ctk_views.EmpleadoMantenimientoView.__new__(ctk_views.EmpleadoMantenimientoView)
    view.db_manager = db
    view.predictivo_listbox = make_dummy_listbox("X")
    called = {}
    monkeypatch.setattr(ctk_views.messagebox, "showerror", lambda *a, **k: called.setdefault("err", True))
    view._cargar_predictivo_list = lambda: called.setdefault("load", True)
    view._marcar_revisado()
    assert "err" in called
    assert not any("INSERT INTO Mantenimiento" in q for q in db.queries)


def test_marcar_revisado_inserts_when_available(monkeypatch):
    db = DummyDB(state=1)
    view = ctk_views.EmpleadoMantenimientoView.__new__(ctk_views.EmpleadoMantenimientoView)
    view.db_manager = db
    view.predictivo_listbox = make_dummy_listbox("X")
    called = {}
    monkeypatch.setattr(ctk_views.messagebox, "showinfo", lambda *a, **k: called.setdefault("ok", True))
    view._cargar_predictivo_list = lambda: called.setdefault("load", True)
    view._marcar_revisado()
    assert "ok" in called
    assert any("INSERT INTO Mantenimiento" in q for q in db.queries)
