import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.dual_db_manager import DualDBManager

class DummyConn:
    def cursor(self):
        class C:
            def execute(self, *a, **k):
                pass
            def close(self):
                pass
            def fetchall(self):
                return []
        return C()
    def close(self):
        pass


def test_retry_pending_skips_without_updated(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'test.db')
    db = DualDBManager()
    db.pending = [('remote2', 'INSERT INTO t (a) VALUES (%s)', (1,))]
    db.remote1_active = True
    db.remote2_active = False

    called = []
    monkeypatch.setattr(db, '_exec_mysql', lambda *a, **k: called.append(a))
    monkeypatch.setattr(db, 'connect_remote2', lambda: DummyConn())

    db.retry_pending()
    assert called == []
    assert db.pending == []


def test_worker_cycle_replays_on_recovery(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'test.db')
    db = DualDBManager()
    db.pending = [('remote1', 'UPDATE t SET val=%s, updated_at=%s WHERE id=%s', (1, '2024', 1))]
    db.remote1_active = False
    db.remote2_active = True

    executed = []
    monkeypatch.setattr(db, '_exec_mysql', lambda *a, **k: executed.append(a))

    def conn1():
        db.remote1_active = True
        return DummyConn()
    monkeypatch.setattr(db, 'connect_remote1', conn1)
    monkeypatch.setattr(db, 'connect_remote2', lambda: DummyConn())

    db._worker_cycle()

    assert executed
    assert db.pending == []
