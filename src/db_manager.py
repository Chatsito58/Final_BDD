import os
import logging
import pymysql
from dotenv import load_dotenv

from .sqlite_manager import SQLiteManager


class DBManager:
    """Router that tries to use MariaDB and falls back to SQLite."""

    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.offline = False
        self._sqlite = SQLiteManager()

    def connect(self):
        """Return a connection to the active database."""
        if self.offline:
            return self._sqlite.connect()

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
            self.offline = True
            return self._sqlite.connect()

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
                conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception as exc:
            print(f"[DBManager] Error ejecutando consulta: {exc}")
            if not self.offline:
                self.offline = True
                return self._sqlite.execute_query(query, params, fetch)
            return None

    def save_pending_reservation(self, data):
        """Persist reservation data in the local SQLite database."""
        self._sqlite.save_pending_reservation(data)

    def sync_pending_reservations(self):
        """Attempt to push locally stored reservations and payments to MariaDB."""
        if self.offline:
            self.logger.info("[DBManager] Sincronización omitida, modo sin conexión")
            return

        # Connect directly to MariaDB
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
            conn = pymysql.connect(**config)
        except Exception as exc:
            self.logger.error(f"[DBManager] Error conectando a MariaDB: {exc}")
            self.offline = True
            return

        cursor = conn.cursor()

        # Synchronize reservations
        reservas = self._sqlite.get_pending_reservations() or []
        for res in reservas:
            insert_q = (
                "INSERT INTO Alquiler "
                "(fecha_hora_salida, fecha_hora_entrada, id_vehiculo, "
                "id_cliente, id_seguro, id_estado) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            params = (res[1], res[2], res[3], res[4], res[5], res[6])
            try:
                cursor.execute(insert_q, params)
                self._sqlite.delete_reservation(res[0])
                self.logger.info(f"[DBManager] Sincronizada reserva {res[0]}")
            except Exception as exc:
                self.logger.error(f"[DBManager] Error insertando reserva {res[0]}: {exc}")
                conn.close()
                return

        # Synchronize payments (abonos)
        abonos = self._sqlite.get_pending_abonos() or []
        for ab in abonos:
            insert_a = (
                "INSERT INTO Abono_reserva "
                "(valor, fecha_hora, id_reserva, id_medio_pago) "
                "VALUES (%s, %s, %s, %s)"
            )
            params = (ab[1], ab[2], ab[3], 1)
            try:
                cursor.execute(insert_a, params)
                self._sqlite.delete_abono(ab[0])
                self.logger.info(f"[DBManager] Sincronizado abono {ab[0]}")
            except Exception as exc:
                self.logger.error(f"[DBManager] Error insertando abono {ab[0]}: {exc}")
                conn.close()
                return

        cursor.close()
        conn.close()
        self.logger.info("[DBManager] Sincronización finalizada")

    def close(self):
        """Placeholder to keep API compatibility."""
        # Connections are opened and closed per query
        pass
