import os
import sqlite3
from dotenv import load_dotenv


class SQLiteManager:
    """Simple SQLite database manager."""

    def __init__(self):
        load_dotenv()
        self.db_path = os.getenv("LOCAL_DB_PATH", "local.db")

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_path)
            print("[SQLiteManager] Conexión exitosa a SQLite")
            return conn
        except sqlite3.Error as exc:
            print(f"[SQLiteManager] Error de conexión a SQLite: {exc}")
            return None

    def execute_query(self, query, params=None, fetch=True):
        try:
            conn = self.connect()
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
            cursor.close()
            conn.close()
            return result
        except sqlite3.Error as exc:
            print(f"[SQLiteManager] Error ejecutando consulta: {exc}")
            return None

    def save_pending_reservation(self, data):
        """Persist reservation data locally."""
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

