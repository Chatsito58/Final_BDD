"""Database helper module that falls back to SQLite when MariaDB is unavailable."""

from mysql import connector
from mysql.connector import Error
import sqlite3
import json

from . import config


class DBManager:
    """Manage database connections and queries using config variables."""

    def __init__(self):
        self.config = {
            "host": config.DB_REMOTE_HOST,
            "user": config.DB_REMOTE_USER,
            "password": config.DB_REMOTE_PASSWORD,
            "database": config.DB_REMOTE_NAME,
        }
        self._connection = None
        self._sqlite_conn = None
        self.use_sqlite = False
        self._init_sqlite()

    def _init_sqlite(self):
        """Create the local SQLite database and pending reservations table."""
        self._sqlite_conn = sqlite3.connect(config.RUTA_DB_LOCAL)
        self._sqlite_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservas_pendientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datos TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._sqlite_conn.commit()

    def _get_sqlite_connection(self):
        if self._sqlite_conn is None:
            self._init_sqlite()
        return self._sqlite_conn

    def get_connection(self):
        """Return a connection to MariaDB or SQLite if the remote is unavailable."""
        if not self.use_sqlite:
            try:
                if self._connection is None or not self._connection.is_connected():
                    self._connection = connector.connect(**self.config)
                return self._connection
            except Error:
                self.use_sqlite = True
        return self._get_sqlite_connection()

    # Backwards compatibility with previous API
    connect = get_connection

    def execute_query(self, query, params=None):
        """Execute a parameterized query using the available backend."""
        conn = self.get_connection()
        cursor = conn.cursor()
        sql = query
        if self.use_sqlite:
            # Convert param style for SQLite
            sql = query.replace("%s", "?")
        try:
            cursor.execute(sql, params or [])
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        except Exception as exc:
            if not self.use_sqlite:
                # If remote execution fails, fallback to sqlite
                self.use_sqlite = True
                cursor.close()
                return self.execute_query(query, params)
            # On sqlite failure just raise
            if hasattr(conn, "rollback"):
                conn.rollback()
            raise exc
        finally:
            cursor.close()

    def save_pending_reservation(self, datos):
        """Store reservation info locally as pending."""
        conn = self._get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reservas_pendientes (datos) VALUES (?)",
            (json.dumps(datos),)
        )
        conn.commit()
        cursor.close()

