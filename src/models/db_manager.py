try:
    import mysql.connector as pymysql
except Exception:  # pragma: no cover - fallback if mysql connector missing
    pymysql = None
import os
from src.sqlite_manager import SQLiteManager

class DBManager:
    def __init__(self, logger):
        self.logger = logger
        self.offline = pymysql is None
        self._sqlite = SQLiteManager()

    def is_sqlite(self):
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
            self.logger.warning("Fallo crítico: usando modo offline (SQLite)")
            self.offline = True
            return self._sqlite.connect()

    def execute_query(self, query, params=None, fetch=True):
        try:
            conn = self.connect()
            # Detectar motor y ajustar placeholders (por si el modo cambió)
            if self.is_sqlite():
                query = query.replace('%s', '?')
            if conn is None:
                self.logger.error("No se pudo establecer conexión con la base de datos")
                self.logger.warning("Consulta abortada por falta de conexión")
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
            self.logger.warning("Consulta fallida: %s", query)
            if not self.offline:
                self.offline = True
                return self._sqlite.execute_query(query.replace('%s', '?'), params, fetch)
            return None

    def save_pending_reservation(self, data):
        return self._sqlite.save_pending_reservation(data) 