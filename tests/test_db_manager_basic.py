import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.db_manager import DBManager


class DummyConn:
    def __init__(self):
        self.autocommit = True

    def close(self):
        pass

    def cursor(self):
        class C:
            def execute(self, *a, **k):
                pass

            def fetchall(self):
                return []

            def close(self):
                pass

        return C()


def test_goes_offline_on_connect_failure(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'local.db')
    import src.db_manager as db_module

    def fail_connect(**kwargs):
        raise Exception('down')

    mysql_mock = types.SimpleNamespace(connector=types.SimpleNamespace(connect=fail_connect))
    monkeypatch.setattr(db_module, 'mysql', mysql_mock, raising=False)

    db = db_module.DBManager()
    assert db.offline is True


def test_reconnect_triggers_sync(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'local.db')
    import src.db_manager as db_module

    def fail_connect(**kwargs):
        raise Exception('down')

    mysql_mock = types.SimpleNamespace(connector=types.SimpleNamespace(connect=fail_connect))
    monkeypatch.setattr(db_module, 'mysql', mysql_mock, raising=False)

    db = db_module.DBManager()
    assert db.offline

    calls = []

    def success_connect(**kwargs):
        return DummyConn()

    mysql_online = types.SimpleNamespace(connector=types.SimpleNamespace(connect=success_connect))
    monkeypatch.setattr(db_module, 'mysql', mysql_online, raising=False)
    monkeypatch.setattr(db, 'sync_pending_reservations', lambda: calls.append('sync'))
    monkeypatch.setattr(db, 'sync_critical_data_to_local', lambda: calls.append('critical'))

    assert db.try_reconnect() is True
    assert db.offline is False
    assert 'sync' in calls and 'critical' in calls
