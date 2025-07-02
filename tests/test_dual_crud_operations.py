import os
import sys
import types
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.dual_db_manager import DualDBManager


class DummyConn:
    def cursor(self):
        class C:
            def execute(self, *a, **k):
                pass
            def fetchall(self):
                return [('dummy',)]
            def close(self):
                pass
            @property
            def lastrowid(self):
                return 1
        return C()
    def close(self):
        pass


def test_crud_writes_to_both(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'dual.db')
    db = DualDBManager()

    executed = []
    def fake_exec(conn, q, p=None, fetch=True, last=False):
        executed.append((q, p, last, conn))
        return 1 if last else None

    monkeypatch.setattr(db, '_exec_mysql', fake_exec)
    monkeypatch.setattr(db, 'connect_remote1', lambda: DummyConn())
    monkeypatch.setattr(db, 'connect_remote2', lambda: DummyConn())

    db.insert("INSERT INTO Estado_reserva(descripcion) VALUES (%s)", ('nuevo',))
    db.update(
        "UPDATE Estado_reserva SET descripcion=%s WHERE id_estado=%s",
        ('editado', 1),
    )
    db.delete("DELETE FROM Estado_reserva WHERE id_estado=%s", (1,))

    assert len(executed) == 6
    assert db.pending == []


def test_queue_and_replay(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'dual.db')
    db = DualDBManager()

    executed = []
    conn1 = DummyConn()
    conn2 = DummyConn()
    fail = {'val': True}

    def fake_exec(conn, q, p=None, fetch=True, last=False):
        if conn is conn2 and fail['val']:
            fail['val'] = False
            raise Exception('down')
        executed.append((conn, q, p, last))
        return 1 if last else None

    monkeypatch.setattr(db, '_exec_mysql', fake_exec)
    monkeypatch.setattr(db, 'connect_remote1', lambda: conn1)
    monkeypatch.setattr(db, 'connect_remote2', lambda: conn2)

    q = "INSERT INTO Estado_reserva(descripcion) VALUES (%s)"
    params = ('pendiente',)
    db.insert(q, params)

    assert len(executed) == 1
    assert executed[0][1] == q
    assert db.pending == [('remote2', q, params)]

    monkeypatch.setattr(db, 'connect_remote2', lambda: DummyConn())
    db.retry_pending()

    assert len(executed) >= 2
    assert db.pending == []


def test_select_secondary_when_primary_down(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'dual.db')
    db = DualDBManager()

    monkeypatch.setattr(db, 'connect_remote1', lambda: None)
    monkeypatch.setattr(db, 'connect_remote2', lambda: DummyConn())
    monkeypatch.setattr(db, '_exec_mysql', lambda *a, **k: [('ok',)])
    monkeypatch.setattr(db, '_exec_sqlite', lambda *a, **k: pytest.fail('sqlite'))

    rows = db.select('SELECT 1')
    assert rows == [('ok',)]


def test_local_takeover_when_all_offline(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'dual.db')
    db = DualDBManager()

    monkeypatch.setattr(db, 'connect_remote1', lambda: None)
    monkeypatch.setattr(db, 'connect_remote2', lambda: None)

    local_calls = []
    orig_sql = db._exec_sqlite
    def wrap_sql(q, p=None, fetch=True, last=False):
        local_calls.append((q, p, last))
        return orig_sql(q, p, fetch, last)
    monkeypatch.setattr(db, '_exec_sqlite', wrap_sql)

    db.insert(
        "INSERT INTO Estado_reserva(descripcion) VALUES (%s)",
        ('local',),
    )

    rows = db.sqlite.execute_query(
        "SELECT descripcion FROM Estado_reserva WHERE descripcion = ?",
        ('local',),
    )
    assert rows == [('local',)]
    assert len(local_calls) == 1
    assert len(db.pending) == 2

    monkeypatch.setattr(db, '_exec_mysql', lambda *a, **k: pytest.fail('mysql'))
    res = db.select(
        "SELECT descripcion FROM Estado_reserva WHERE descripcion=%s",
        ('local',),
    )
    assert res == [('local',)]
