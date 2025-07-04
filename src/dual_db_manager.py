import os
import json
import logging
import threading
from dotenv import load_dotenv

try:
    import mysql.connector
except Exception:
    mysql = None

from .sqlite_manager import SQLiteManager


class DualDBManager:
    """Manage two remote MySQL databases with local SQLite fallback."""

    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.sqlite = SQLiteManager()
        self.pending = []  # [(target, query, params)]
        self.remote1_active = False
        self.remote2_active = False
        self._thread = None
        self._stop_event = threading.Event()
        self._interval = 20 * 60  # 20 minutes by default

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def _config_remote1(self):
        return {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'port': os.getenv('DB_REMOTE_PORT', 3306),
            'connection_timeout': 10,
        }

    def _config_remote2(self):
        return {
            'host': os.getenv('DB_REMOTE_HOST2'),
            'user': os.getenv('DB_REMOTE_USER2'),
            'password': os.getenv('DB_REMOTE_PASSWORD2'),
            'database': os.getenv('DB_REMOTE_NAME2'),
            'port': os.getenv('DB_REMOTE_PORT2', 3306),
            'connection_timeout': 10,
        }

    def connect_remote1(self):
        if mysql is None:
            self.remote1_active = False
            return None
        try:
            conn = mysql.connector.connect(**self._config_remote1())
            conn.autocommit = True
            self.remote1_active = True
            return conn
        except Exception as exc:
            self.logger.error("Remote1 connection failed: %s", exc)
            self.remote1_active = False
            return None

    def connect_remote2(self):
        if mysql is None:
            self.remote2_active = False
            return None
        try:
            conn = mysql.connector.connect(**self._config_remote2())
            conn.autocommit = True
            self.remote2_active = True
            return conn
        except Exception as exc:
            self.logger.error("Remote2 connection failed: %s", exc)
            self.remote2_active = False
            return None

    # ------------------------------------------------------------------
    # Internal execution
    # ------------------------------------------------------------------
    def _exec_mysql(self, conn, query, params=None, fetch=True, last=False):
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if last:
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
        cursor.close()
        conn.close()
        return result

    def _exec_sqlite(self, query, params=None, fetch=True, last=False):
        query = query.replace('%s', '?')
        return self.sqlite.execute_query(
            query, params, fetch=fetch, return_lastrowid=last
        )

    def _enqueue(self, target, query, params):
        self.pending.append((target, query, params))

    # ------------------------------------------------------------------
    # Retry queue helpers
    # ------------------------------------------------------------------
    def enqueue_failed_operation(self, operation, table_name, payload, target):
        """Store a failed write operation in the SQLite retry queue."""
        data = json.dumps(payload)
        query = (
            "INSERT INTO retry_queue (operation, table_name, payload, target, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))"
        )
        self.sqlite.execute_query(query, (operation, table_name, data, target), fetch=False)

    def fetch_retry_queue(self):
        """Return all pending retry entries as a list of dictionaries."""
        rows = self.sqlite.execute_query(
            "SELECT id, operation, table_name, payload, target FROM retry_queue ORDER BY id"
        ) or []
        result = []
        for row in rows:
            payload = json.loads(row[3]) if row[3] else None
            result.append(
                {
                    "id": row[0],
                    "operation": row[1],
                    "table_name": row[2],
                    "payload": payload,
                    "target": row[4],
                }
            )
        return result

    def delete_retry_entry(self, entry_id):
        """Remove an entry from the retry queue."""
        self.sqlite.execute_query(
            "DELETE FROM retry_queue WHERE id = ?", (entry_id,), fetch=False
        )

    # ------------------------------------------------------------------
    # CRUD public API
    # ------------------------------------------------------------------
    def insert(self, query, params=None):
        return self._write(query, params, last=True)

    def update(self, query, params=None):
        return self._write(query, params, last=False)

    def delete(self, query, params=None):
        return self._write(query, params, last=False)

    def select(self, query, params=None):
        # Try remote1 -> remote2 -> sqlite
        if self.remote1_active or self.remote1_active is False:
            conn = self.connect_remote1()
            if conn:
                try:
                    return self._exec_mysql(conn, query, params, fetch=True)
                except Exception as exc:  # pragma: no cover - network errors
                    self.logger.error("Select remote1 failed: %s", exc)
                    self.remote1_active = False
        conn2 = self.connect_remote2()
        if conn2:
            try:
                return self._exec_mysql(conn2, query, params, fetch=True)
            except Exception as exc:  # pragma: no cover - network errors
                self.logger.error("Select remote2 failed: %s", exc)
                self.remote2_active = False
        # Fallback to SQLite
        return self._exec_sqlite(query, params, fetch=True)

    # ------------------------------------------------------------------
    # Write with dual replication
    # ------------------------------------------------------------------
    def _write(self, query, params, last):
        result = None

        conn1 = self.connect_remote1()
        if conn1:
            try:
                # Execute on primary remote
                result = self._exec_mysql(conn1, query, params, fetch=False, last=last)

                # Replicate to secondary remote if available
                conn2 = self.connect_remote2()
                if conn2:
                    try:
                        self._exec_mysql(conn2, query, params, fetch=False, last=False)
                    except Exception as exc:  # pragma: no cover - network errors
                        self.logger.error("Replicate to remote2 failed: %s", exc)
                        self.remote2_active = False
                        self._enqueue('remote2', query, params)
                else:
                    # queue if remote2 could not connect
                    self._enqueue('remote2', query, params)

                # Always replicate locally when remote1 succeeds
                self._exec_sqlite(query, params, fetch=False, last=False)
                return result

            except Exception as exc:  # pragma: no cover - network errors
                self.logger.error("Write remote1 failed: %s", exc)
                self.remote1_active = False
                # Fall through to try remote2

        conn2 = self.connect_remote2()
        if conn2:
            try:
                # Execute on secondary remote
                result = self._exec_mysql(conn2, query, params, fetch=False, last=last)

                # Queue operation for remote1 recovery
                self._enqueue('remote1', query, params)

                # Replicate locally as this write succeeded
                self._exec_sqlite(query, params, fetch=False, last=False)
                return result

            except Exception as exc:  # pragma: no cover - network errors
                self.logger.error("Write remote2 failed: %s", exc)
                self.remote2_active = False

        # both remotes failed -> write locally and queue for later
        local_result = self._exec_sqlite(query, params, fetch=False, last=last)
        self._enqueue('remote1', query, params)
        self._enqueue('remote2', query, params)
        if last:
            result = local_result

        return result

    # ------------------------------------------------------------------
    # Retry pending operations
    # ------------------------------------------------------------------
    def retry_pending(self):
        remaining = []
        for target, query, params in self.pending:
            if target == 'remote1':
                conn = self.connect_remote1()
            else:
                conn = self.connect_remote2()
            if conn:
                try:
                    # Skip operations without updated_at when another server
                    # stayed online to avoid overwriting newer data.
                    has_updated = False
                    if isinstance(params, dict):
                        has_updated = 'updated_at' in params
                    other_online = (
                        self.remote2_active if target == 'remote1' else self.remote1_active
                    )
                    if not has_updated and other_online and 'updated_at' not in query.lower():
                        continue
                    self._exec_mysql(conn, query, params, fetch=False)
                    continue
                except Exception as exc:  # pragma: no cover - network errors
                    self.logger.error("Retry %s failed: %s", target, exc)
            remaining.append((target, query, params))
        self.pending = remaining

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------
    def _worker_cycle(self):
        prev1 = self.remote1_active
        prev2 = self.remote2_active

        conn1 = self.connect_remote1()
        if conn1:
            conn1.close()

        conn2 = self.connect_remote2()
        if conn2:
            conn2.close()

        recovered1 = not prev1 and self.remote1_active
        recovered2 = not prev2 and self.remote2_active

        if recovered1 or recovered2:
            self.retry_pending()

    def _worker_loop(self):
        while not self._stop_event.is_set():
            self._worker_cycle()
            self._stop_event.wait(self._interval)

    def start_worker(self, interval_minutes=20):
        """Start the background synchronization thread."""
        self._interval = interval_minutes * 60
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def stop_worker(self):
        """Stop the background synchronization thread."""
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join()
        self._thread = None
