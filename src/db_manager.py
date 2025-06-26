import os
from mysql import connector
from mysql.connector import Error
from dotenv import load_dotenv


class DBManager:
    """Simple database manager for MariaDB connections."""

    def __init__(self):
        load_dotenv()
        self.config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
        }
        self._connection = None

    def connect(self):
        """Establish and return a database connection."""
        if self._connection is None or not self._connection.is_connected():
            self._connection = connector.connect(**self.config)
        return self._connection

    def execute_query(self, query, params=None, fetch=True):
        """Execute a SQL query and optionally fetch results."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall() if fetch else None
            conn.commit()
            cursor.close()
            return result
        except Error as exc:
            print(f"Database query error: {exc}")
            if self._connection and self._connection.is_connected():
                self._connection.rollback()
            return None

    def save_pending_reservation(self, data):
        """Persist reservation data locally when the remote DB is unreachable."""
        import json
        from pathlib import Path

        pending_file = Path(__file__).resolve().parents[1] / 'data' / 'pending_reservations.json'

        reservations = []
        if pending_file.exists():
            with pending_file.open('r', encoding='utf-8') as fh:
                try:
                    reservations = json.load(fh)
                except json.JSONDecodeError:
                    reservations = []

        reservations.append(data)

        pending_file.parent.mkdir(parents=True, exist_ok=True)
        with pending_file.open('w', encoding='utf-8') as fh:
            json.dump(reservations, fh, ensure_ascii=False, indent=2)

    def close(self):
        """Close the active connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
