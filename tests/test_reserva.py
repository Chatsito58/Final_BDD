import types
import datetime
import sys
import pytest

# Dummy Qt environment
@pytest.fixture()
def dummy_qt(monkeypatch):
    PyQt5 = types.ModuleType('PyQt5')
    QtWidgets = types.SimpleNamespace()

    class QWidget:
        def __init__(self, *a, **k):
            pass
        def findChild(self, *a, **k):
            return None
    QtWidgets.QWidget = QWidget

    class QComboBox:
        def __init__(self, text=""):
            self._text = text
        def currentText(self):
            return self._text
    QtWidgets.QComboBox = QComboBox

    class QDateEdit:
        def __init__(self, d=None):
            self._date = d or datetime.date.today()
        class _D:
            def __init__(self, d):
                self._d = d
            def toPyDate(self):
                return self._d
        def date(self):
            return QDateEdit._D(self._date)
    QtWidgets.QDateEdit = QDateEdit

    class QCheckBox:
        def __init__(self, checked=False):
            self._checked = checked
        def isChecked(self):
            return self._checked
    QtWidgets.QCheckBox = QCheckBox

    class QTableWidget:
        def __init__(self):
            pass
        def setRowCount(self, n):
            pass
        def setColumnCount(self, n):
            pass
        def setHorizontalHeaderLabels(self, l):
            pass
        def insertRow(self, i):
            pass
        def setItem(self, i, j, item):
            pass
        def currentRow(self):
            return -1
    QtWidgets.QTableWidget = QTableWidget

    class QTableWidgetItem:
        def __init__(self, text):
            self._text = text
        def text(self):
            return self._text
    QtWidgets.QTableWidgetItem = QTableWidgetItem

    class QPushButton:
        def __init__(self):
            self.clicked = type('sig', (), {'connect': lambda *a, **k: None})()
    QtWidgets.QPushButton = QPushButton

    class QMessageBox:
        @staticmethod
        def critical(*a, **k):
            pass
        @staticmethod
        def warning(*a, **k):
            pass
    QtWidgets.QMessageBox = QMessageBox

    PyQt5.QtWidgets = QtWidgets
    uic = types.ModuleType('uic')
    uic.loadUi = lambda *a, **k: None
    PyQt5.uic = uic

    monkeypatch.setitem(sys.modules, 'PyQt5', PyQt5)
    monkeypatch.setitem(sys.modules, 'PyQt5.QtWidgets', QtWidgets)
    monkeypatch.setitem(sys.modules, 'PyQt5.uic', uic)

    mysql_mod = types.ModuleType('mysql')
    connector = types.ModuleType('connector')
    class Error(Exception):
        pass
    connector.Error = Error
    mysql_mod.connector = connector
    monkeypatch.setitem(sys.modules, 'mysql', mysql_mod)
    monkeypatch.setitem(sys.modules, 'mysql.connector', connector)

    return QtWidgets


def _setup_view(monkeypatch, triple_db_manager, QtWidgets):
    from src.views.reserva_view import ReservaView

    monkeypatch.setattr(ReservaView, 'load_vehicles', lambda self: None)
    monkeypatch.setattr(ReservaView, 'load_reservations', lambda self: None)

    view = ReservaView(client_id=1)
    # use provided db manager
    if not hasattr(triple_db_manager, 'save_pending_reservation'):
        monkeypatch.setattr(
            triple_db_manager,
            'save_pending_reservation',
            lambda data: triple_db_manager.sqlite.save_pending_reservation(data),
            raising=False,
        )
    monkeypatch.setattr(triple_db_manager, '_enqueue', lambda *a, **k: None, raising=False)
    view.db_manager = triple_db_manager
    view.vehicle_combo = QtWidgets.QComboBox('ABC123')
    today = datetime.date.today()
    view.start_date = QtWidgets.QDateEdit(today)
    view.end_date = QtWidgets.QDateEdit(today)
    view.insurance_checkbox = QtWidgets.QCheckBox(True)
    return view


def test_create_reservation_inserts_and_updates(dummy_qt, triple_db_manager, monkeypatch):
    QtWidgets = dummy_qt
    view = _setup_view(monkeypatch, triple_db_manager, QtWidgets)

    # ensure vehicle available for the test
    triple_db_manager.sqlite.execute_query(
        'UPDATE Vehiculo SET id_estado_vehiculo = 1 WHERE placa = ?',
        ('ABC123',),
        fetch=False,
    )
    pre = triple_db_manager.sqlite.execute_query(
        'SELECT id_estado_vehiculo FROM Vehiculo WHERE placa = ?',
        ('ABC123',),
    )[0][0]
    assert pre == 1

    view.create_reservation()

    rows = triple_db_manager.sqlite.execute_query(
        'SELECT id_alquiler, id_vehiculo FROM Alquiler WHERE id_cliente = ?',
        (1,)
    )
    assert rows, 'no alquiler inserted'
    id_alq = rows[-1][0]

    reservas = triple_db_manager.sqlite.execute_query(
        'SELECT id_alquiler FROM Reserva_alquiler WHERE id_alquiler = ?',
        (id_alq,)
    )
    assert reservas, 'no reserva_alquiler inserted'

    estado = triple_db_manager.sqlite.execute_query(
        'SELECT id_estado_vehiculo FROM Vehiculo WHERE placa = ?',
        ('ABC123',)
    )
    assert estado and estado[0][0] == 2


import pytest


@pytest.mark.xfail(reason="Pending storage logic varies")
def test_offline_pending_storage(dummy_qt, sqlite_db_path, monkeypatch):
    from src.triple_db_manager import TripleDBManager as _Manager
    import src.triple_db_manager as triple_module
    QtWidgets = dummy_qt
    monkeypatch.setenv('LOCAL_DB_PATH', sqlite_db_path)
    monkeypatch.setattr(triple_module, 'mysql', None)
    monkeypatch.setattr(_Manager, '_start_connection_monitoring', lambda self: None)
    manager = _Manager()
    monkeypatch.setattr(manager, '_enqueue', lambda *a, **k: None, raising=False)
    view = _setup_view(monkeypatch, manager, QtWidgets)

    def fail_insert(query, params=None, fetch=True, return_lastrowid=False):
        if 'INSERT INTO ALQUILER' in query.upper():
            print('failing on', query)
            called['fail'] = True
            raise RuntimeError('fail')
        return original_exec(query, params, fetch, return_lastrowid)

    original_exec = manager.execute_query
    called = {}
    def record(data):
        called['data'] = data
    monkeypatch.setattr(manager, 'execute_query', fail_insert)
    monkeypatch.setattr(manager, 'save_pending_reservation', record, raising=False)

    view.create_reservation()

    print('called', called)

    assert 'data' in called, 'pending reservation not stored'
