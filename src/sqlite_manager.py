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
        inserts = Path(__file__).resolve().parents[1] / 'data' / 'inserts_sqlite.sql'
        
        conn = sqlite3.connect(self.db_path)
        
        if schema.exists():
            with schema.open('r', encoding='utf-8') as fh:
                conn.executescript(fh.read())
        
        if inserts.exists():
            with inserts.open('r', encoding='utf-8') as fh:
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

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        try:
            conn = self.connect()
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if return_lastrowid:
                last_id = cursor.lastrowid
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
            cursor.close()
            conn.close()
            if return_lastrowid:
                return last_id
            return result
        except sqlite3.Error as exc:
            print(f"[SQLiteManager] Error ejecutando consulta: {exc}")
            return None

    def get_lastrowid(self, table_name):
        """Obtener el último ID insertado en una tabla específica."""
        try:
            conn = self.connect()
            if conn is None:
                return None
            cursor = conn.cursor()
            # Obtener el último ID insertado en la tabla
            # Mapear nombres de tabla a nombres de columna ID
            id_column_map = {
                'Alquiler': 'id_alquiler',
                'Reserva': 'id_reserva',
                'Cliente': 'id_cliente',
                'Empleado': 'id_empleado',
                'Usuario': 'id_usuario',
                'Abono': 'id_abono',
                'Reserva_alquiler': 'id_reserva',
                'Abono_reserva': 'id_abono'
            }
            id_column = id_column_map.get(table_name, f'id_{table_name.lower()}')
            cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result and result[0] else None
        except sqlite3.Error as exc:
            print(f"[SQLiteManager] Error obteniendo lastrowid para tabla {table_name}: {exc}")
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

    def get_pending_reservations(self):
        """Return all reservations marked as pending."""
        query = (
            "SELECT id_reserva, fecha_hora_salida, fecha_hora_entrada, "
            "id_vehiculo, id_cliente, id_seguro, id_estado "
            "FROM Reserva WHERE pendiente = 1"
        )
        return self.execute_query(query)

    def delete_reservation(self, reserva_id):
        """Remove a reservation from the local database."""
        query = "DELETE FROM Reserva WHERE id_reserva = ?"
        self.execute_query(query, (reserva_id,), fetch=False)

    def get_pending_abonos(self):
        """Return all payments marked as pending."""
        query = (
            "SELECT id_abono, valor, fecha_hora, id_reserva "
            "FROM Abono WHERE pendiente = 1"
        )
        return self.execute_query(query)

    def delete_abono(self, abono_id):
        """Remove a payment from the local database."""
        query = "DELETE FROM Abono WHERE id_abono = ?"
        self.execute_query(query, (abono_id,), fetch=False)

