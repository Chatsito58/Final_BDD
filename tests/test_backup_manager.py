import os
import builtins
from pathlib import Path

import pytest

from src.backup_manager import BackupManager


def test_backup_on_startup_ok(monkeypatch, tmp_path):
    db_path = tmp_path / "db.sqlite"
    db_path.write_text("data")
    backup_dir = tmp_path / "backups"
    mgr = BackupManager(db_path=db_path, backup_dir=backup_dir)

    monkeypatch.setattr(mgr, "verify_database_integrity", lambda: True)
    called = {}
    def fake_create(bt):
        called["backup"] = bt
        return "bk"
    monkeypatch.setattr(mgr, "create_backup", fake_create)

    result = mgr.backup_on_startup()
    assert result == "bk"
    assert called["backup"] == "startup"


def test_backup_on_startup_restores(monkeypatch, tmp_path):
    db_path = tmp_path / "db.sqlite"
    db_path.write_text("data")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    b1 = backup_dir / "backup_startup_a.db"
    b1.write_text("1")
    os.utime(b1, (1, 1))
    b2 = backup_dir / "backup_shutdown_b.db"
    b2.write_text("2")
    os.utime(b2, (2, 2))

    mgr = BackupManager(db_path=db_path, backup_dir=backup_dir)
    monkeypatch.setattr(mgr, "verify_database_integrity", lambda: False)

    restored = {}
    def fake_restore(p):
        restored["path"] = Path(p)
    monkeypatch.setattr(mgr, "restore_from_backup", fake_restore)

    monkeypatch.setattr(mgr, "create_backup", lambda t: "bk")

    result = mgr.backup_on_startup()
    assert result == "bk"
    assert restored["path"] == b2


def test_backup_on_startup_creates_new_db(monkeypatch, tmp_path):
    db_path = tmp_path / "db.sqlite"
    backup_dir = tmp_path / "backups"
    mgr = BackupManager(db_path=db_path, backup_dir=backup_dir)
    monkeypatch.setattr(mgr, "verify_database_integrity", lambda: False)
    monkeypatch.setattr(mgr, "get_latest_backup", lambda t: None)
    monkeypatch.setattr(mgr, "restore_from_backup", lambda p: None)
    monkeypatch.setattr(mgr, "create_backup", lambda t: "bk")

    assert not db_path.exists()
    result = mgr.backup_on_startup()
    assert result == "bk"
    assert db_path.exists()


def test_cleanup_respects_max_backups(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db_path.write_text("x")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    mgr = BackupManager(db_path=db_path, backup_dir=backup_dir, max_backups=3)

    for i in range(5):
        f = backup_dir / f"backup_startup_{i}.db"
        f.write_text(str(i))
        os.utime(f, (i, i))

    mgr.cleanup_old_backups("startup")
    names = {p.name for p in backup_dir.iterdir()}
    assert len(names) == 3
    assert names == {f"backup_startup_{i}.db" for i in [4, 3, 2]}


def test_cleanup_compresses_when_low_disk(monkeypatch, tmp_path):
    db_path = tmp_path / "db.sqlite"
    db_path.write_text("x")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    mgr = BackupManager(db_path=db_path, backup_dir=backup_dir, max_backups=4)

    for i in range(4):
        f = backup_dir / f"backup_startup_{i}.db"
        f.write_text(str(i))
        os.utime(f, (i, i))

    monkeypatch.setattr(mgr, "_disk_space_low", lambda ratio=0.1: True)
    mgr.cleanup_old_backups("startup")

    assert (backup_dir / "backup_startup_0.db.gz").exists()
    assert not (backup_dir / "backup_startup_0.db").exists()

