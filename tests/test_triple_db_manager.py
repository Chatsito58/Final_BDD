import types
import pytest

from src.triple_db_manager import TripleDBManager


class FakeSQLite:
    def __init__(self):
        self.queue = []
        self.ops = []
        self.counter = 0

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        self.ops.append(query)
        if "INSERT INTO retry_queue" in query:
            self.counter += 1
            self.queue.append({
                "id": self.counter,
                "operation": params[0],
                "table_name": params[1],
                "payload": params[2],
                "target": params[3],
            })
            return self.counter if return_lastrowid else None
        if query.startswith("SELECT id, operation, payload, target"):
            return [
                (e["id"], e["operation"], e["payload"], e["target"])
                for e in self.queue
            ]
        if query.startswith("DELETE FROM retry_queue"):
            del_id = params[0]
            self.queue = [e for e in self.queue if e["id"] != del_id]
            return None
        # Local writes
        if return_lastrowid:
            self.counter += 1
            return self.counter
        return []


def setup_db(monkeypatch, r1_up=True, r2_up=True):
    db = TripleDBManager()
    db.sqlite = FakeSQLite()
    operations = []

    def fake_exec_mysql(self, conn, query, params=None, fetch=True, last=False):
        operations.append((conn, query, params, last))
        if last:
            return 1
        return None

    monkeypatch.setattr(db, "_exec_mysql", types.MethodType(fake_exec_mysql, db))

    def connect1():
        db.remote1_active = r1_up
        return "r1" if r1_up else None

    def connect2():
        db.remote2_active = r2_up
        return "r2" if r2_up else None

    monkeypatch.setattr(db, "connect_remote1", connect1)
    monkeypatch.setattr(db, "connect_remote2", connect2)
    return db, operations


def test_write_with_one_remote_down(monkeypatch):
    db, ops = setup_db(monkeypatch, r1_up=False, r2_up=True)
    db.insert("INSERT INTO Cliente (nombre) VALUES (%s)", ("Ana",))

    # Operation executed on remote2 and locally
    assert any(o[0] == "r2" for o in ops)
    assert any("Cliente" in q for q in db.sqlite.ops)

    # Queue contains entry for remote1
    assert db.pending == [
        (1, "remote1", "INSERT INTO Cliente (nombre) VALUES (%s)", ("Ana",))
    ]
    assert len(db.sqlite.queue) == 1
    assert db.sqlite.queue[0]["target"] == "remote1"


def test_retry_flushes_pending(monkeypatch):
    db, ops = setup_db(monkeypatch, r1_up=False, r2_up=True)
    db.insert("INSERT INTO Cliente (nombre) VALUES (%s)", ("Ana",))

    # Remote1 was down, so one entry queued
    assert len(db.pending) == 1

    # Recover remote1
    def connect1():
        db.remote1_active = True
        return "r1"

    db.remote2_active = False
    monkeypatch.setattr(db, "connect_remote1", connect1)

    db.retry_pending()

    # Pending should be cleared and entry removed from sqlite
    assert db.pending == []
    assert db.sqlite.queue == []
    # Should have executed on remote1
    assert any(o[0] == "r1" for o in ops)
