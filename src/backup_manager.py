import os
import shutil
import sqlite3
from datetime import datetime
import logging
from dotenv import load_dotenv


class BackupManager:
    """Handle SQLite database backups with rotation and integrity checks."""

    def __init__(self, db_path=None, backup_dir=None):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path or os.getenv("LOCAL_DB_PATH", "data/local.sqlite")
        if backup_dir is None:
            base_dir = os.path.dirname(self.db_path)
            backup_dir = os.path.join(base_dir, "backups")
        self.backup_dir = backup_dir
        self.ensure_backup_dir()

    def ensure_backup_dir(self):
        """Create the backup directory if it doesn't exist."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
            self.logger.info("Created backup directory: %s", self.backup_dir)

    def _has_enough_space(self):
        """Return True if there is enough free disk space for a copy."""
        usage = shutil.disk_usage(self.backup_dir)
        db_size = os.path.getsize(self.db_path)
        if usage.free < db_size:
            self.logger.error(
                "Not enough disk space: required %s bytes, only %s free",
                db_size,
                usage.free,
            )
            return False
        return True

    def create_backup(self, backup_type):
        """Create a timestamped backup of the database."""
        self.ensure_backup_dir()
        if not self._has_enough_space():
            return None
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name = f"backup_{backup_type}_{timestamp}.db"
        dest = os.path.join(self.backup_dir, name)
        try:
            shutil.copy2(self.db_path, dest)
            self.logger.info("Backup created: %s", dest)
            self.cleanup_old_backups(backup_type)
            return dest
        except Exception as exc:
            self.logger.error("Failed to create backup: %s", exc)
            return None

    def cleanup_old_backups(self, backup_type):
        """Keep only the three most recent backups for the given type."""
        pattern = f"backup_{backup_type}_"
        files = [
            os.path.join(self.backup_dir, f)
            for f in os.listdir(self.backup_dir)
            if f.startswith(pattern)
        ]
        files.sort(key=os.path.getmtime, reverse=True)
        for old in files[3:]:
            try:
                os.remove(old)
                self.logger.info("Removed old backup: %s", old)
            except Exception as exc:
                self.logger.error("Failed to remove old backup %s: %s", old, exc)

    def restore_from_backup(self, backup_file):
        """Restore the database from the specified backup file."""
        try:
            shutil.copy2(backup_file, self.db_path)
            self.logger.info("Database restored from %s", backup_file)
        except Exception as exc:
            self.logger.error("Failed to restore from backup %s: %s", backup_file, exc)

    def verify_database_integrity(self):
        """Run PRAGMA integrity_check on the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check")
            result = cur.fetchone()
            conn.close()
            ok = result and result[0] == "ok"
            if not ok:
                self.logger.error("Integrity check failed: %s", result)
            else:
                self.logger.info("Integrity check passed")
            return ok
        except Exception as exc:
            self.logger.error("Integrity check error: %s", exc)
            return False

    def get_latest_backup(self, backup_type):
        """Return the most recent backup path for the given type."""
        pattern = f"backup_{backup_type}_"
        backups = [
            os.path.join(self.backup_dir, f)
            for f in os.listdir(self.backup_dir)
            if f.startswith(pattern)
        ]
        if not backups:
            return None
        latest = max(backups, key=os.path.getmtime)
        return latest

    def backup_on_startup(self):
        """Create a backup if integrity check succeeds."""
        self.logger.info("Running startup backup")
        if self.verify_database_integrity():
            return self.create_backup("startup")
        self.logger.error("Startup backup skipped due to integrity error")
        return None

    def backup_on_shutdown(self):
        """Create a backup when application shuts down."""
        self.logger.info("Running shutdown backup")
        return self.create_backup("shutdown")
