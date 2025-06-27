import os
import logging
try:
    import mysql.connector as pymysql
except Exception:  # pragma: no cover - if connector missing
    pymysql = None
from dotenv import load_dotenv

from .sqlite_manager import SQLiteManager


class DBManager:
    """Router that tries to use MariaDB and falls back to SQLite."""

    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.offline = pymysql is None
        self._sqlite = SQLiteManager()

    def is_sqlite(self):
        """Return True if operating in offline SQLite mode."""
        return self.offline

    def connect(self):
        """Return a connection to the active database."""
        if self.offline:
            return self._sqlite.connect()

        if pymysql is None:
            self.logger.warning("Driver de MySQL no disponible, usando modo offline")
            self.offline = True
            return self._sqlite.connect()

        config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'connection_timeout': 3,
            'autocommit': True,
        }
        try:
            connection = pymysql.connect(**config)
            self.logger.info("Conexión exitosa a la base de datos")
            return connection
        except Exception as exc:
            self.logger.error("Error de conexión a la base de datos: %s", exc)
            self.offline = True
            return self._sqlite.connect()

    def execute_query(self, query, params=None, fetch=True):
        try:
            conn = self.connect()
            if self.is_sqlite():
                query = query.replace('%s', '?')
            if conn is None:
                self.logger.error("No se pudo establecer conexión con la base de datos")
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
            self.logger.error("Error ejecutando consulta: %s", exc)
            if not self.offline:
                self.offline = True
                return self._sqlite.execute_query(query.replace('%s', '?'), params, fetch)
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
            'connection_timeout': 3,
            'autocommit': True,
        }
        try:
            conn = pymysql.connect(**config)
        except Exception as exc:
            self.logger.error("[DBManager] Error conectando a MariaDB: %s", exc)
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
                self.logger.info("[DBManager] Sincronizada reserva %s", res[0])
            except Exception as exc:
                self.logger.error(
                    "[DBManager] Error insertando reserva %s: %s", res[0], exc
                )
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
                self.logger.info("[DBManager] Sincronizado abono %s", ab[0])
            except Exception as exc:
                self.logger.error(
                    "[DBManager] Error insertando abono %s: %s", ab[0], exc
                )
                conn.close()
                return

        cursor.close()
        conn.close()
        self.logger.info("[DBManager] Sincronización finalizada")

    def close(self):
        """Placeholder to keep API compatibility."""
        # Connections are opened and closed per query
        pass
