import os
import pymysql
from dotenv import load_dotenv


class DBManager:
    """Gestor simple de base de datos para MariaDB usando PyMySQL."""

    def __init__(self):
        pass  # No se guarda ninguna variable de instancia

    def connect(self):
        load_dotenv()
        config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'connect_timeout': 3,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.Cursor,
            'autocommit': True,
        }
        try:
            connection = pymysql.connect(**config)
            print("[DBManager] ¡Conexión exitosa a la base de datos!")
            return connection
        except Exception as exc:
            print(f"[DBManager] Error de conexión a la base de datos: {exc}")
            return None

    def execute_query(self, query, params=None, fetch=True):
        try:
            conn = self.connect()
            if conn is None:
                print("[DBManager] No se pudo establecer conexión con la base de datos")
                return None
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                result = None
            cursor.close()
            conn.close()
            return result
        except Exception as exc:
            print(f"[DBManager] Error ejecutando consulta: {exc}")
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
