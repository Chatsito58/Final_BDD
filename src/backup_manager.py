import os
import shutil
import sqlite3
from datetime import datetime
import logging
import gzip
from dotenv import load_dotenv


class BackupManager:
    """Handle SQLite database backups with rotation and integrity checks."""

    def __init__(self, db_path=None, backup_dir=None, max_backups=3):
        load_dotenv()

        self.logger = logging.getLogger(__name__)
        self.db_path = db_path or os.getenv("LOCAL_DB_PATH", "data/local.sqlite")
        if backup_dir is None:
            base_dir = os.path.dirname(self.db_path)
            backup_dir = os.path.join(base_dir, "backups")
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.logger.info("Initializing BackupManager: db=%s, dir=%s", self.db_path, self.backup_dir)
        self.ensure_backup_dir()

    def ensure_backup_dir(self):
        """Create the backup directory if it doesn't exist."""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, exist_ok=True)
                self.logger.info("Created backup directory: %s", self.backup_dir)
            else:
                self.logger.info("Backup directory exists: %s", self.backup_dir)
        except Exception as exc:
            self.logger.error("Failed to ensure backup directory %s: %s", self.backup_dir, exc)

    def _has_enough_space(self):
        """Return True if there is enough free disk space for a copy."""
        try:
            usage = shutil.disk_usage(self.backup_dir)
            db_size = os.path.getsize(self.db_path)
            self.logger.info("Free space: %s bytes", usage.free)
            if usage.free < db_size:
                self.logger.error(
                    "Not enough disk space: required %s bytes, only %s free",
                    db_size,
                    usage.free,
                )
                return False
            return True
        except Exception as exc:
            self.logger.error("Failed to check disk space: %s", exc)
            return False

    def _disk_space_low(self, ratio=0.1):
        """Return True if free space is below the given ratio of total."""
        try:
            usage = shutil.disk_usage(self.backup_dir)
            return usage.free < usage.total * ratio
        except Exception as exc:
            self.logger.error("Failed to check disk space: %s", exc)
            return False

    def create_backup(self, backup_type):
        """Create a timestamped backup of the database."""
        self.logger.info("Starting %s backup", backup_type)
        try:
            self.ensure_backup_dir()
            if not self._has_enough_space():
                return None
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            name = f"backup_{backup_type}_{timestamp}.db"
            dest = os.path.join(self.backup_dir, name)
            shutil.copy2(self.db_path, dest)
            self.logger.info("Backup created: %s", dest)
            self.cleanup_old_backups(backup_type)
            return dest
        except Exception as exc:
            self.logger.error("Failed to create backup: %s", exc)
            return None

    def cleanup_old_backups(self, backup_type):
        """Remove excess backups and optionally compress older ones."""
        self.logger.info("Cleaning up old backups for type %s", backup_type)
        try:
            pattern = f"backup_{backup_type}_"
            files = [
                os.path.join(self.backup_dir, f)
                for f in os.listdir(self.backup_dir)
                if f.startswith(pattern)
            ]
            files.sort(key=os.path.getmtime, reverse=True)

            for old in files[self.max_backups:]:
                try:
                    os.remove(old)
                    self.logger.info("Removed old backup: %s", old)
                except Exception as exc:
                    self.logger.error("Failed to remove old backup %s: %s", old, exc)

            if self._disk_space_low():
                for path in files[3:]:
                    if path.endswith(".gz"):
                        continue
                    gz_path = f"{path}.gz"
                    try:
                        with open(path, "rb") as src, gzip.open(gz_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        os.remove(path)
                        self.logger.info("Compressed old backup: %s", gz_path)
                    except Exception as exc:
                        self.logger.error("Failed to compress backup %s: %s", path, exc)
        except Exception as exc:
            self.logger.error("Failed to cleanup old backups: %s", exc)

    def restore_from_backup(self, backup_file):
        """Restore the database from the specified backup file."""
        self.logger.info("Restoring database from %s", backup_file)
        try:
            shutil.copy2(backup_file, self.db_path)
            self.logger.info("Database restored from %s", backup_file)
        except Exception as exc:
            self.logger.error("Failed to restore from backup %s: %s", backup_file, exc)

    def verify_database_integrity(self):
        """Run PRAGMA integrity_check on the database."""
        self.logger.info("Running integrity check")
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
        self.logger.info("Searching latest %s backup", backup_type)
        try:
            pattern = f"backup_{backup_type}_"
            backups = [
                os.path.join(self.backup_dir, f)
                for f in os.listdir(self.backup_dir)
                if f.startswith(pattern)
            ]
            if not backups:
                return None
            latest = max(backups, key=os.path.getmtime)
            self.logger.info("Latest backup found: %s", latest)
            return latest
        except Exception as exc:
            self.logger.error("Failed to get latest backup: %s", exc)
            return None

    def backup_on_startup(self):
        """Verify database integrity and create a startup backup.

        If the integrity check fails, attempt to recover the database using the
        most recent backup (either from a previous startup or shutdown). When
        no backups are found, an empty database file is created. A new startup
        backup is created at the end of the process regardless of whether a
        restoration was needed.
        """

        self.logger.info("Running startup backup")
        try:
            if not self.verify_database_integrity():
                self.logger.warning("Database corrupted, attempting recovery")
                latest_startup = self.get_latest_backup("startup")
                latest_shutdown = self.get_latest_backup("shutdown")
                candidates = [p for p in [latest_startup, latest_shutdown] if p]

                if candidates:
                    latest = max(candidates, key=os.path.getmtime)
                    self.logger.info("Restoring database from %s", latest)
                    self.restore_from_backup(latest)
                else:
                    open(self.db_path, "w").close()
                    self.logger.warning(
                        "No valid backups found. Created new empty database: %s",
                        self.db_path,
                    )

            return self.create_backup("startup")
        except Exception as exc:
            self.logger.error("Startup backup failed: %s", exc)
            return None

    def backup_on_shutdown(self):
        """Create a backup when application shuts down."""
        self.logger.info("Running shutdown backup")
        try:
            return self.create_backup("shutdown")
        except Exception as exc:
            self.logger.error("Shutdown backup failed: %s", exc)
            return None
