import os
import logging
import traceback
try:
    import mysql.connector
except Exception:  # pragma: no cover - if connector missing
    mysql = None
from dotenv import load_dotenv

from .sqlite_manager import SQLiteManager


class DBManager:
    """Router that tries to use MariaDB and falls back to SQLite."""

    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.offline = False  # Inicializa en modo remoto por defecto
        self._sqlite = SQLiteManager()

    def is_sqlite(self):
        """Return True if operating in offline SQLite mode."""
        return self.offline

    def connect(self):
        """Return a connection to the active database."""
        self.logger.info("=== Iniciando método connect ===")
        self.logger.info(f"Modo offline: {self.offline}")
        
        if self.offline:
            self.logger.info("Usando modo offline, conectando a SQLite...")
            return self._sqlite.connect()

        if mysql is None:
            self.logger.warning("Driver de MySQL no disponible, usando modo offline")
            self.offline = True
            return self._sqlite.connect()

        self.logger.info("Configurando conexión a MySQL/MariaDB...")
        config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'port': 3306,  # Puerto por defecto de MySQL/MariaDB
            'connection_timeout': 10,  # Aumentar timeout a 10 segundos
        }
        
        self.logger.info(f"Configuración de conexión:")
        self.logger.info(f"  Host: {config['host']}")
        self.logger.info(f"  User: {config['user']}")
        self.logger.info(f"  Database: {config['database']}")
        self.logger.info(f"  Timeout: {config['connection_timeout']}")
        
        try:
            self.logger.info("[DEBUG] Antes de conectar con mysql.connector.connect()")
            print("[DEBUG] Antes de conectar con mysql.connector.connect()")
            connection = mysql.connector.connect(**config)
            self.logger.info("[DEBUG] Conexión creada, antes de autocommit")
            print("[DEBUG] Conexión creada, antes de autocommit")
            connection.autocommit = True
            self.logger.info("[DEBUG] Autocommit activado")
            print("[DEBUG] Autocommit activado")
            self.logger.info("Conexión exitosa a la base de datos")
            print("[DEBUG] Conexión exitosa a la base de datos")
            return connection
        except Exception as exc:
            self.logger.error(f"Error de conexión a la base de datos: {exc}")
            self.logger.error(traceback.format_exc())
            try:
                import PyQt5.QtWidgets as QtWidgets
                QtWidgets.QMessageBox.critical(None, "Error de conexión", f"{exc}\n\n{traceback.format_exc()}")
            except Exception as e:
                self.logger.error(f"No se pudo mostrar el QMessageBox: {e}")
            self.logger.info("Cambiando a modo offline...")
            self.offline = True
            return self._sqlite.connect()

    def execute_query(self, query, params=None, fetch=True):
        try:
            self.logger.info(f"Ejecutando consulta: {query}")
            self.logger.info(f"Parámetros: {params}")
            self.logger.info(f"Modo offline: {self.offline}")
            
            self.logger.info("Intentando conectar a la base de datos...")
            conn = self.connect()
            self.logger.info(f"Conexión establecida: {conn is not None}")
            
            if self.is_sqlite():
                query = query.replace('%s', '?')
                self.logger.info(f"Consulta adaptada para SQLite: {query}")
            
            if conn is None:
                self.logger.error("No se pudo establecer conexión con la base de datos")
                return None
                
            self.logger.info("Creando cursor...")
            cursor = conn.cursor()
            self.logger.info("Cursor creado exitosamente")
            
            self.logger.info("Ejecutando consulta en la base de datos...")
            cursor.execute(query, params or ())
            self.logger.info("Consulta ejecutada exitosamente en la base de datos")
            
            if fetch:
                self.logger.info("Obteniendo resultados...")
                result = cursor.fetchall()
                self.logger.info(f"Resultado obtenido: {result}")
            else:
                result = None
                conn.commit()
                self.logger.info("Cambios confirmados en la base de datos")
                
            self.logger.info("Cerrando cursor...")
            cursor.close()
            self.logger.info("Cerrando conexión...")
            conn.close()
            self.logger.info("Conexión cerrada exitosamente")
            return result
        except Exception as exc:
            self.logger.error(f"Error ejecutando consulta: {exc}")
            self.logger.error(f"Tipo de error: {type(exc).__name__}")
            self.logger.error(traceback.format_exc())
            if not self.offline:
                self.logger.info("Cambiando a modo offline...")
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
            'port': 3306,  # Puerto por defecto de MySQL/MariaDB
            'connection_timeout': 10,  # Aumentar timeout a 10 segundos
        }
        try:
            conn = mysql.connector.connect(**config)
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
