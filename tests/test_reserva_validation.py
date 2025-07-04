import pytest

try:  # Skip if GUI libs missing
    import customtkinter  # noqa: F401
    from PyQt5 import QtWidgets
except Exception:  # pragma: no cover - dependency missing
    pytest.skip("GUI libraries not installed", allow_module_level=True)

from datetime import date

from src.views import ctk_views
from src.views.reserva_view import ReservaView


class DummyDB:
    def __init__(self, state=1):
        self.state = state
        self.queries = []

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        self.queries.append(query)
        if "SELECT id_estado_vehiculo" in query:
            return [(self.state,)]
        return []

    def save_pending_reservation(self, datos):
        self.saved = datos


def make_dummy_date(d):
    class D:
        def date(self_inner):
            class Q:
                def toPyDate(self):
                    return d
            return Q()
    return D()


def make_dummy_combo(text):
    class C:
        def currentText(self):
            return text
    return C()


def make_dummy_check(value=False):
    class B:
        def isChecked(self):
            return value
    return B()


def test_create_reservation_checks_vehicle_state(monkeypatch):
    db = DummyDB(state=2)
    view = ReservaView.__new__(ReservaView)
    view.db_manager = db
    view.client_id = 5
    view.vehicle_combo = make_dummy_combo("X")
    view.start_date = make_dummy_date(date(2023, 1, 1))
    view.end_date = make_dummy_date(date(2023, 1, 2))
    view.insurance_checkbox = make_dummy_check(False)
    view.sucursal_id = 1
    called = {}
    monkeypatch.setattr(QtWidgets.QMessageBox, "warning", lambda *a, **k: called.setdefault("warn", True))
    view.load_reservations = lambda: called.setdefault("load", True)
    view.create_reservation()
    assert "warn" in called
    assert not any("INSERT INTO Alquiler" in q for q in db.queries)


def test_actualizar_reserva_checks_vehicle_state(monkeypatch):
    db = DummyDB(state=2)
    view = ctk_views.ClienteView.__new__(ctk_views.ClienteView)
    view.db_manager = db
    view._cargar_reservas_cliente = lambda *_: None
    view._cargar_reservas_pendientes = lambda *_: None
    called = {}
    monkeypatch.setattr(ctk_views.messagebox, "showerror", lambda *a, **k: called.setdefault("err", True))
    ok = ctk_views.ClienteView._actualizar_reserva(view, 1, "2023-01-01 10:00", "2023-01-02 10:00", "X", None, None)
    assert not ok
    assert "err" in called
    assert any("SELECT id_estado_vehiculo" in q for q in db.queries)
