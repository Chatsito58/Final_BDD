import os
import re
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.backup_manager import BackupManager


def _init_db(path: Path):
    """Create a minimal SQLite database with one table and row."""
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO t(name) VALUES ('demo')")
    conn.commit()
    conn.close()


def test_create_backup_creates_file(monkeypatch):
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "db.sqlite"
        _init_db(db_path)
        backup_dir = Path(tmp) / "backups"
        mgr = BackupManager(db_path=db_path, backup_dir=backup_dir)
        monkeypatch.setattr(mgr, "_has_enough_space", lambda: True)

        backup = mgr.create_backup("startup")
        assert backup is not None
        backup_path = Path(backup)
        assert backup_path.exists()
        assert backup_path.parent == backup_dir
        assert re.match(r"backup_startup_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.db", backup_path.name)


def test_cleanup_old_backups_keeps_three():
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "db.sqlite"
        db_path.write_text("x")
        backup_dir = Path(tmp) / "backups"
        backup_dir.mkdir()
        mgr = BackupManager(db_path=db_path, backup_dir=backup_dir, max_backups=3)

        for i in range(5):
            f = backup_dir / f"backup_startup_{i}.db"
            f.write_text(str(i))
            os.utime(f, (i, i))

        mgr.cleanup_old_backups("startup")
        remaining = {p.name for p in backup_dir.iterdir()}
        assert len(remaining) == 3
        assert remaining == {f"backup_startup_{i}.db" for i in [4, 3, 2]}


def test_verify_database_integrity_valid_and_corrupt():
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "db.sqlite"
        _init_db(db_path)
        mgr = BackupManager(db_path=db_path, backup_dir=Path(tmp) / "backups")
        assert mgr.verify_database_integrity()

        # corrupt the database file
        db_path.write_bytes(b"not a sqlite db")
        assert not mgr.verify_database_integrity()


def test_restore_from_backup(monkeypatch):
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "db.sqlite"
        _init_db(db_path)
        backup_dir = Path(tmp) / "backups"
        mgr = BackupManager(db_path=db_path, backup_dir=backup_dir)
        monkeypatch.setattr(mgr, "_has_enough_space", lambda: True)
        backup = mgr.create_backup("startup")

        # corrupt database
        db_path.write_bytes(b"bad")
        assert not mgr.verify_database_integrity()

        mgr.restore_from_backup(backup)
        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT name FROM t").fetchone()
        conn.close()
        assert row == ("demo",)
