import os
import json
import logging
import threading
import datetime
from dotenv import load_dotenv

try:
    import mysql.connector
except Exception:
    mysql = None

from .sqlite_manager import SQLiteManager


class TripleDBManager:
    """Synchronize two remote MySQL databases and a local SQLite instance.

    The manager replicates every write across the three databases and keeps a
    queue of failed operations to retry automatically. A background thread can
    be started to periodically check connectivity and flush the queue every
    ``DB_WORKER_INTERVAL`` minutes (20 by default).

    Example
    -------
    >>> db = TripleDBManager()
    >>> db.insert("INSERT INTO Cliente (nombre) VALUES (%s)", ("Ana",))
    >>> db.update(
    ...     "UPDATE Cliente SET nombre=%s WHERE id_cliente=%s",
    ...     ("Ana Ruiz", 1),
    ... )
    >>> db.delete("DELETE FROM Cliente WHERE id_cliente=%s", (1,))
    """

    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.connection_logger = logging.getLogger('connection_changes')
        self.sqlite = SQLiteManager()
        # Queue of operations pending to be sent to the remotes.
        # Each item is (row_id, target, query, params) where row_id references
        # the entry persisted in the SQLite retry_queue table.
        self.pending = []  # [(id, target, query, params)]
        self.remote1_active = False
        self.remote2_active = False
        self._thread = None
        self._stop_event = threading.Event()
        self.stop_monitoring = threading.Event()
        self.connection_monitor_thread = None
        self.previous_remote1_state = None
        self.previous_remote2_state = None
        # Interval between connection checks in seconds. Can be overridden with
        # the ``DB_WORKER_INTERVAL`` environment variable (minutes).
        minutes = int(os.getenv("DB_WORKER_INTERVAL", "20"))
        self._interval = minutes * 60

        self._start_connection_monitoring()

    def update_maintenance_states(self):
        """Release vehicles from maintenance whose end date has passed."""
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = (
                "UPDATE Vehiculo SET id_estado_vehiculo = 1 "
                "WHERE id_estado_vehiculo = 3 AND placa IN "
                "(SELECT placa FROM Mantenimiento WHERE fecha_fin <= %s)"
            )
            self.execute_query(query, (now,), fetch=False)
        except Exception as exc:
            # Si la columna fecha_fin no existe, simplemente logear el error y continuar
            self.logger.warning("No se pudo actualizar estados de mantenimiento (posible columna fecha_fin faltante): %s", exc)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def is_remote1_active(self):
        """Return True if the primary remote database is reachable."""
        return self.remote1_active

    def is_remote2_active(self):
        """Return True if the secondary remote database is reachable."""
        return self.remote2_active

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def _config_remote1(self):
        return {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'port': os.getenv('DB_REMOTE_PORT'),
            'connection_timeout': 3,
        }

    def _config_remote2(self):
        return {
            'host': os.getenv('DB_REMOTE_HOST2'),
            'user': os.getenv('DB_REMOTE_USER2'),
            'password': os.getenv('DB_REMOTE_PASSWORD2'),
            'database': os.getenv('DB_REMOTE_NAME2'),
            'port': os.getenv('DB_REMOTE_PORT2'),
            'connection_timeout': 3,
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

    def ping_remote1(self):
        """Attempt a quick connection to remote1 to update its status."""
        if mysql is None:
            self.remote1_active = False
            return False
        config = self._config_remote1().copy()
        config["connection_timeout"] = 2
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
            self.remote1_active = True
            return True
        except Exception as exc:
            self.remote1_active = False
            self.logger.error("Remote1 ping failed: %s", exc)
            return False

    def ping_remote2(self):
        """Attempt a quick connection to remote2 to update its status."""
        if mysql is None:
            self.remote2_active = False
            return False
        config = self._config_remote2().copy()
        config["connection_timeout"] = 2
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
            self.remote2_active = True
            return True
        except Exception as exc:
            self.remote2_active = False
            self.logger.error("Remote2 ping failed: %s", exc)
            return False

    def ping_remotes(self):
        """Check connectivity to both remote databases."""
        self.ping_remote1()
        self.ping_remote2()

    # ------------------------------------------------------------------
    # Connection monitoring helpers
    # ------------------------------------------------------------------
    def _start_connection_monitoring(self):
        """Launch the background thread that checks connection changes."""
        if self.connection_monitor_thread and self.connection_monitor_thread.is_alive():
            return
        self.stop_monitoring.clear()
        self.connection_monitor_thread = threading.Thread(
            target=self._connection_monitor_loop,
            daemon=True,
        )
        self.connection_monitor_thread.start()

    def _connection_monitor_loop(self):
        while not self.stop_monitoring.is_set():
            try:
                self.ping_remote1()
                self.ping_remote2()
                self._check_connection_changes()
            except Exception as exc:  # pragma: no cover - just log
                self.connection_logger.error("Monitor error: %s", exc)
            self.stop_monitoring.wait(5)

    def _check_connection_changes(self):
        """Log whenever the connection state of a remote changes."""
        if self.remote1_active != self.previous_remote1_state:
            state = "online" if self.remote1_active else "offline"
            log = (
                self.connection_logger.info
                if self.remote1_active
                else self.connection_logger.warning
            )
            log("Remote1 is %s", state)
            self.previous_remote1_state = self.remote1_active

        if self.remote2_active != self.previous_remote2_state:
            state = "online" if self.remote2_active else "offline"
            log = (
                self.connection_logger.info
                if self.remote2_active
                else self.connection_logger.warning
            )
            log("Remote2 is %s", state)
            self.previous_remote2_state = self.remote2_active

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
        """Add a failed operation to the in-memory and persistent queues."""
        payload = json.dumps(params)
        insert_q = (
            "INSERT INTO retry_queue (operation, table_name, payload, target, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))"
        )
        row_id = self.sqlite.execute_query(
            insert_q, (query, "", payload, target), fetch=False, return_lastrowid=True
        )
        self.pending.append((row_id, target, query, params))

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
    # Write with triple replication
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
        """Attempt to replay queued operations on the remote servers."""
        rows = self.sqlite.execute_query(
            "SELECT id, operation, payload, target FROM retry_queue ORDER BY id"
        ) or []

        existing = {item[0] for item in self.pending if item[0] is not None}
        entries = [
            (row[0], row[3], row[1], json.loads(row[2]) if row[2] else None)
            for row in rows
            if row[0] not in existing
        ]
        entries.extend(self.pending)

        remaining = []
        for row_id, target, query, params in entries:
            conn = self.connect_remote1() if target == "remote1" else self.connect_remote2()
            if conn:
                try:
                    # Skip operations without updated_at when another server
                    # stayed online to avoid overwriting newer data.
                    has_updated = False
                    if isinstance(params, dict):
                        has_updated = "updated_at" in params
                    other_online = (
                        self.remote2_active if target == "remote1" else self.remote1_active
                    )
                    if (
                        not has_updated
                        and other_online
                        and "updated_at" not in query.lower()
                    ):
                        if row_id:
                            self.delete_retry_entry(row_id)
                        continue
                    self._exec_mysql(conn, query, params, fetch=False)
                    if row_id:
                        self.delete_retry_entry(row_id)
                    continue
                except Exception as exc:  # pragma: no cover - network errors
                    self.logger.error("Retry %s failed: %s", target, exc)
            remaining.append((row_id, target, query, params))
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
        """Start the background synchronization thread.

        Parameters
        ----------
        interval_minutes : int, optional
            Frequency in minutes for connection checks and pending operation
            retries. Defaults to 20 minutes.
        """
        self._interval = interval_minutes * 60
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def stop_worker(self):
        """Stop the background synchronization thread."""
        if self.connection_monitor_thread:
            self.stop_monitoring.set()
            self.connection_monitor_thread.join()
            self.connection_monitor_thread = None
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join()
        self._thread = None

    def try_reconnect(self):
        """Attempt to reconnect to the remote databases."""
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

        return self.remote1_active or self.remote2_active

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    @property
    def offline(self):
        """Return True when no remote database is reachable."""
        return not (self.remote1_active or self.remote2_active)

    def is_sqlite(self):
        """Compatibility wrapper mirroring DBManager.is_sqlite."""
        return self.offline

    def connect(self):
        """Return a connection to either remote server or the local SQLite."""
        conn = self.connect_remote1()
        if conn:
            return conn
        conn = self.connect_remote2()
        if conn:
            return conn
        return self.sqlite.connect()

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        """Execute a query using the high level CRUD API for compatibility."""
        if fetch:
            return self.select(query, params)
        lowered = query.strip().lower()
        if return_lastrowid or lowered.startswith("insert"):
            return self.insert(query, params)
        if lowered.startswith("update"):
            return self.update(query, params)
        if lowered.startswith("delete"):
            return self.delete(query, params)
        # Fallback for other statements
        return self.update(query, params)

    def execute_query_with_headers(self, query, params=None):
        """Execute a query and return results with column headers."""
        result = self.execute_query(query, params)
        if not result:
            return [], []
        
        # Get headers from the first row's keys if it's a dict
        if isinstance(result[0], dict):
            headers = list(result[0].keys())
            rows = [list(row.values()) for row in result]
        else:
            # For tuple results, we don't have headers
            headers = []
            rows = result
        
        return headers, rows

    def save_pending_registro(self, tabla, data):
        """Insertar un registro pendiente en cualquier tabla con columna 'pendiente'."""
        # data: dict con los campos y valores
        campos = ', '.join(data.keys()) + ', pendiente'
        placeholders = ', '.join(['?'] * len(data)) + ', 1'
        query = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"
        params = tuple(data.values())
        self.sqlite.execute_query(query, params, fetch=False)
