import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.dual_db_manager import DualDBManager


class DummyConn:
    """Simple stand-in object for a MySQL connection."""
    pass


def test_live_sync_with_retry(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'dual.db')
    db = DualDBManager()

    conn1 = DummyConn()
    conn2 = DummyConn()
    executed = []
    remote2_fail = {'val': False}

    def fake_exec(conn, query, params=None, fetch=True, last=False):
        executed.append((conn, query, params))
        if conn is conn1:
            db._exec_sqlite(query, params, fetch=False, last=last)
        elif conn is conn2 and remote2_fail['val']:
            remote2_fail['val'] = False
            raise Exception('down')
        return 1 if last else None

    monkeypatch.setattr(db, '_exec_mysql', fake_exec)
    monkeypatch.setattr(db, 'connect_remote1', lambda: conn1)

    def remote2_online():
        db.remote2_active = True
        return conn2

    monkeypatch.setattr(db, 'connect_remote2', remote2_online)

    insert_q = "INSERT INTO Estado_reserva(descripcion) VALUES (%s)"
    db.insert(insert_q, ('nuevo',))

    row = db.sqlite.execute_query(
        "SELECT id_estado FROM Estado_reserva WHERE descripcion=?",
        ('nuevo',)
    )
    inserted_id = row[0][0]

    remote2_fail['val'] = True

    update_q = "UPDATE Estado_reserva SET descripcion=%s WHERE id_estado=%s"
    db.update(update_q, ('editado', inserted_id))

    remote2_fail['val'] = True
    delete_q = "DELETE FROM Estado_reserva WHERE id_estado=%s"
    db.delete(delete_q, (inserted_id,))

    assert db.pending == [
        ('remote2', update_q, ('editado', inserted_id)),
        ('remote2', delete_q, (inserted_id,)),
    ]

    rows = db.sqlite.execute_query(
        "SELECT * FROM Estado_reserva WHERE id_estado=?",
        (inserted_id,)
    )
    assert rows == []

    monkeypatch.setattr(db, 'connect_remote2', remote2_online)
    db.retry_pending()

    remote1_ops = [q for c, q, _ in executed if c is conn1]
    remote2_ops = [q for c, q, _ in executed if c is conn2]

    assert insert_q in remote1_ops and update_q in remote1_ops and delete_q in remote1_ops
    assert insert_q in remote2_ops and update_q in remote2_ops and delete_q in remote2_ops
    assert db.pending == []
