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


def test_eventual_reconnect(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'test.db')
    db = DBManager()
    assert db.offline  # comienza en modo offline por falta de mysql

    events = []
    db.set_on_reconnect_callback(lambda: events.append('callback'))

    monkeypatch.setattr(db, 'sync_pending_reservations', lambda: events.append('pending'))
    monkeypatch.setattr(db, 'sync_critical_data_to_local', lambda: events.append('critical'))

    import src.db_manager as db_module

    def fail_connect(**kwargs):
        raise Exception('no server')

    mysql_mock = types.SimpleNamespace(connector=types.SimpleNamespace(connect=fail_connect))
    monkeypatch.setattr(db_module, 'mysql', mysql_mock, raising=False)

    assert db.try_reconnect() is False
    assert db.offline is True

    def success_connect(**kwargs):
        return DummyConn()
    mysql_mock.connector.connect = success_connect

    assert db.try_reconnect() is True
    assert db.offline is False
    assert 'callback' in events
    assert 'pending' in events and 'critical' in events


def test_try_reconnect_switches_online(monkeypatch, tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'test.db')
    db = DBManager()
    assert db.offline

    import src.db_manager as db_module

    mysql_mock = types.SimpleNamespace(connector=types.SimpleNamespace(connect=lambda **k: DummyConn()))
    monkeypatch.setattr(db_module, 'mysql', mysql_mock, raising=False)

    monkeypatch.setattr(db, 'sync_pending_reservations', lambda: None)
    monkeypatch.setattr(db, 'sync_critical_data_to_local', lambda: None)

    assert db.try_reconnect() is True
    assert db.offline is False
