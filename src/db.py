"""Database helper module for connecting to MariaDB."""

from mysql import connector
from mysql.connector import Error

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

    def get_connection(self):
        """Return a connection to MariaDB or ``None`` if it fails."""
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = connector.connect(**self.config)
            return self._connection
        except Error:
            return None

    def execute_query(self, query, params=None):
        """Execute a parameterized query and return the result."""
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            return result
        except Error as exc:
            # If executing a data-modifying statement fails, rollback
            if conn.is_connected():
                conn.rollback()
            raise exc
        finally:
            cursor.close()

