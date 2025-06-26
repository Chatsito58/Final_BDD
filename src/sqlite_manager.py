import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv


class SQLiteManager:
    """Simple SQLite database manager."""

    def __init__(self):
        load_dotenv()
        self.db_path = os.getenv("LOCAL_DB_PATH", "local.db")
        self._initialize_db()

    def _initialize_db(self):
        """Ensure required tables exist."""
        schema = Path(__file__).resolve().parents[1] / 'data' / 'sqlite_schema.sql'
        if not schema.exists():
            return
        conn = sqlite3.connect(self.db_path)
        with schema.open('r', encoding='utf-8') as fh:
            conn.executescript(fh.read())
        conn.close()

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
        """Insert a reservation locally marked as pending."""
        query = (
            "INSERT INTO Reserva "
            "(fecha_hora_salida, fecha_hora_entrada, id_vehiculo, "
            "id_cliente, id_seguro, id_estado, pendiente) "
            "VALUES (?, ?, ?, ?, ?, ?, 1)"
        )
        params = (
            data.get("fecha_hora_salida"),
            data.get("fecha_hora_entrada"),
            data.get("id_vehiculo"),
            data.get("id_cliente"),
            data.get("id_seguro"),
            data.get("id_estado"),
        )
        self.execute_query(query, params, fetch=False)

