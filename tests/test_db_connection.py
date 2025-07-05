from types import SimpleNamespace

import pytest

from src.triple_db_manager import TripleDBManager
import src.triple_db_manager as triple_module


class DummyConn:
    def close(self):
        pass


def test_offline_and_reconnect(monkeypatch, sqlite_db_path):
    """TripleDBManager should enter offline mode then recover."""

    monkeypatch.setattr(TripleDBManager, "_start_connection_monitoring", lambda self: None)

    def fail_connect(*args, **kwargs):
        raise Exception("fail")

    failing_mysql = SimpleNamespace(connector=SimpleNamespace(connect=fail_connect))
    monkeypatch.setattr(triple_module, "mysql", failing_mysql)

    manager = TripleDBManager()

    assert manager.remote1_active is False
    assert manager.remote2_active is False
    assert manager.offline is True

    def success_connect(*args, **kwargs):
        return DummyConn()

    working_mysql = SimpleNamespace(connector=SimpleNamespace(connect=success_connect))
    monkeypatch.setattr(triple_module, "mysql", working_mysql)

    assert manager.try_reconnect() is True
    assert manager.offline is False
