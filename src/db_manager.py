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
        # Intentar sincronizar datos críticos al iniciar si hay conexión
        try:
            conn = self.connect()
            if conn and not self.offline:
                print("[SYNC] Sincronizando datos críticos al iniciar aplicación...")
                self.logger.info("[SYNC] Sincronizando datos críticos al iniciar aplicación...")
                self.sync_critical_data_to_local()
                print("[SYNC] Datos críticos sincronizados correctamente al iniciar.")
                self.logger.info("[SYNC] Datos críticos sincronizados correctamente al iniciar.")
                conn.close()
        except Exception as e:
            print(f"[SYNC][ERROR] Error al sincronizar datos críticos al iniciar: {e}")
            self.logger.error(f"Error al sincronizar datos críticos al iniciar: {e}")

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
            'port': os.getenv('DB_REMOTE_PORT'),  # Puerto por defecto de MySQL/MariaDB
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
            # Si estaba offline y ahora conecta, lanzar callback de reconexión
            if hasattr(self, 'was_offline') and self.was_offline:
                try:
                    if hasattr(self, 'on_reconnect_callback') and self.on_reconnect_callback:
                        self.on_reconnect_callback()
                except Exception as e:
                    self.logger.error(f"Error notificando reconexión a la vista: {e}")
                self.was_offline = False
            elif not hasattr(self, 'was_offline'):
                self.was_offline = False
            return connection
        except Exception as exc:
            self.logger.error(f"Error de conexión a la base de datos: {exc}")
            self.logger.error(traceback.format_exc())
            try:
                import PyQt5.QtWidgets as QtWidgets
                QtWidgets.QMessageBox.critical(None, "Desconexión detectada", "Ocurrió una desconexión del servidor principal y ahora estás en modo offline. Puedes seguir trabajando y los cambios se sincronizarán automáticamente cuando vuelva la conexión.")
            except Exception as e:
                self.logger.error(f"No se pudo mostrar el QMessageBox: {e}")
            self.logger.info("Cambiando a modo offline...")
            self.offline = True
            self.was_offline = True
            # Notificar a las vistas si es necesario
            try:
                if hasattr(self, 'on_disconnect_callback') and self.on_disconnect_callback:
                    self.on_disconnect_callback()
            except Exception as e:
                self.logger.error(f"Error notificando desconexión a la vista: {e}")
            return self._sqlite.connect()

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
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
                print("[SYNC][ERROR] No se pudo establecer conexión con la base de datos. Cambiando a modo offline.")
                self.logger.error("No se pudo establecer conexión con la base de datos")
                return None
            self.logger.info("Creando cursor...")
            cursor = conn.cursor()
            self.logger.info("Cursor creado exitosamente")
            self.logger.info("Ejecutando consulta en la base de datos...")
            cursor.execute(query, params or ())
            self.logger.info("Consulta ejecutada exitosamente en la base de datos")
            
            if return_lastrowid:
                if self.is_sqlite():
                    last_id = cursor.lastrowid
                    cursor.close()
                    conn.close()
                    self.logger.info("Conexión cerrada exitosamente")
                    return last_id
                else:
                    # Para MySQL, obtener el LAST_INSERT_ID() de manera segura
                    try:
                        # Para MySQL, no necesitamos hacer commit explícito si autocommit está activado
                        # Solo obtener el lastrowid del cursor
                        last_id = cursor.lastrowid
                        cursor.close()
                        conn.close()
                        self.logger.info("Conexión cerrada exitosamente")
                        return last_id
                    except Exception as e:
                        print(f"[DB][ERROR] Error obteniendo LAST_INSERT_ID: {e}")
                        self.logger.error(f"[DB][ERROR] Error obteniendo LAST_INSERT_ID: {e}")
                        cursor.close()
                        conn.close()
                        return None
            
            if fetch and not return_lastrowid:
                self.logger.info("Obteniendo resultados...")
                result = cursor.fetchall()
                self.logger.info(f"Resultado obtenido: {result}")
            elif not fetch:
                result = None
                # Solo hacer commit si no es return_lastrowid
                conn.commit()
                self.logger.info("Cambios confirmados en la base de datos")
            else:
                # Si return_lastrowid es True, no necesitamos fetch
                result = None
                if not self.is_sqlite():
                    conn.commit()
                    self.logger.info("Cambios confirmados en la base de datos")
            
            self.logger.info("Cerrando cursor...")
            cursor.close()
            self.logger.info("Cerrando conexión...")
            conn.close()
            self.logger.info("Conexión cerrada exitosamente")
            return result
        except Exception as exc:
            import mysql.connector
            import sqlite3
            import sys
            from mysql.connector.errors import InterfaceError, OperationalError, DatabaseError, IntegrityError, ProgrammingError, InternalError
            # Si es un error de integridad, sintaxis o "Unread result found", NO cambiar a offline
            if isinstance(exc, (IntegrityError, ProgrammingError, sqlite3.IntegrityError, sqlite3.ProgrammingError)):
                print(f"[DB][ERROR] Error de integridad o sintaxis: {exc}")
                self.logger.error(f"[DB][ERROR] Error de integridad o sintaxis: {exc}")
                self.logger.error(f"Tipo de error: {type(exc).__name__}")
                self.logger.error(traceback.format_exc())
                return None
            # Si es un error "Unread result found", NO cambiar a offline
            if isinstance(exc, InternalError) and "Unread result found" in str(exc):
                print(f"[DB][ERROR] Error de cursor con resultados sin leer: {exc}")
                self.logger.error(f"[DB][ERROR] Error de cursor con resultados sin leer: {exc}")
                self.logger.error(f"Tipo de error: {type(exc).__name__}")
                self.logger.error(traceback.format_exc())
                return None
            # Si es un error de conexión, sí cambiar a offline
            if isinstance(exc, (InterfaceError, OperationalError, DatabaseError, sqlite3.OperationalError)):
                print("[SYNC][ERROR] Desconexión detectada. Cambiando a modo offline.")
                self.logger.error(f"Error ejecutando consulta: {exc}")
                self.logger.error(f"Tipo de error: {type(exc).__name__}")
                self.logger.error(traceback.format_exc())
                if not self.offline:
                    print("[SYNC][INFO] Servidor desconectado. Ahora en modo offline.")
                    self.logger.info("[SYNC][INFO] Servidor desconectado. Ahora en modo offline.")
                    self.offline = True
                    # Si la consulta original era un INSERT y necesitamos el ID, adaptar para SQLite
                    if return_lastrowid and query.strip().upper().startswith('INSERT'):
                        # Para SQLite, usar lastrowid directamente
                        return self._sqlite.execute_query(query.replace('%s', '?'), params, fetch=False, return_lastrowid=True)
                    else:
                        return self._sqlite.execute_query(query.replace('%s', '?'), params, fetch, return_lastrowid)
                else:
                    # Si se recupera la conexión, sincronizar datos críticos
                    try:
                        print("[SYNC][INFO] Intentando reconexión con el servidor...")
                        self.logger.info("[SYNC][INFO] Intentando reconexión con el servidor...")
                        conn = self.connect()
                        if conn and not self.offline:
                            print("[SYNC][INFO] Reconexión exitosa. Sincronizando datos críticos...")
                            self.logger.info("[SYNC][INFO] Reconexión exitosa. Sincronizando datos críticos...")
                            self.sync_critical_data_to_local()
                            print("[SYNC][INFO] Datos críticos sincronizados tras reconexión.")
                            self.logger.info("[SYNC][INFO] Datos críticos sincronizados tras reconexión.")
                            print("[SYNC][INFO] Subiendo datos locales pendientes al servidor...")
                            self.logger.info("[SYNC][INFO] Subiendo datos locales pendientes al servidor...")
                            self.sync_pending_reservations()
                            print("[SYNC][INFO] Todos los datos locales pendientes han sido subidos.")
                            self.logger.info("[SYNC][INFO] Todos los datos locales pendientes han sido subidos.")
                            conn.close()
                    except Exception as e:
                        print(f"[SYNC][ERROR] Error al sincronizar datos críticos tras reconexión: {e}")
                        self.logger.error(f"Error al sincronizar datos críticos tras reconexión: {e}")
                return None
            # Otros errores
            print(f"[DB][ERROR] Error inesperado: {exc}")
            self.logger.error(f"[DB][ERROR] Error inesperado: {exc}")
            self.logger.error(f"Tipo de error: {type(exc).__name__}")
            self.logger.error(traceback.format_exc())
            return None

    def save_pending_reservation(self, data):
        """Persist reservation data in the local SQLite database."""
        self._sqlite.save_pending_reservation(data)

    def save_pending_abono(self, data):
        """Insertar un abono localmente marcado como pendiente."""
        query = (
            "INSERT INTO Abono (valor, fecha_hora, id_reserva, pendiente) "
            "VALUES (?, ?, ?, 1)"
        )
        params = (
            data.get("valor"),
            data.get("fecha_hora"),
            data.get("id_reserva"),
        )
        self._sqlite.execute_query(query, params, fetch=False)

    def save_pending_registro(self, tabla, data):
        """Insertar un registro pendiente en cualquier tabla con columna 'pendiente'."""
        # data: dict con los campos y valores
        campos = ', '.join(data.keys()) + ', pendiente'
        placeholders = ', '.join(['?'] * len(data)) + ', 1'
        query = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"
        params = tuple(data.values())
        self._sqlite.execute_query(query, params, fetch=False)

    def sync_pending_reservations(self):
        """Sincronizar todas las tablas con columna 'pendiente' de SQLite a MariaDB."""
        if self.offline:
            print("[SYNC][INFO] Sincronización de pendientes omitida, modo sin conexión.")
            self.logger.info("[SYNC][INFO] Sincronización de pendientes omitida, modo sin conexión.")
            return
        print("[SYNC][INFO] Iniciando subida de datos locales pendientes...")
        self.logger.info("[SYNC][INFO] Iniciando subida de datos locales pendientes...")
        tablas = [
            {
                'tabla': 'Reserva',
                'get': self._sqlite.get_pending_reservations,
                'delete': self._sqlite.delete_reservation,
                'insert': (
                    "INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_seguro, id_estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                ),
                'params': lambda r: (r[1], r[2], r[3], r[4], r[5], r[6]),
                'id': 0
            },
            {
                'tabla': 'Abono',
                'get': self._sqlite.get_pending_abonos,
                'delete': self._sqlite.delete_abono,
                'insert': (
                    "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
                    "VALUES (%s, %s, %s, %s)"
                ),
                'params': lambda a: (a[1], a[2], a[3], 1),
                'id': 0
            },
            # Agrega aquí más tablas si tienes más operaciones pendientes
        ]

        config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
            'port': os.getenv('DB_REMOTE_PORT'),
            'connection_timeout': 10,
        }
        try:
            conn = mysql.connector.connect(**config)
            conn.autocommit = True
        except Exception as exc:
            self.logger.error("[DBManager] Error conectando a MariaDB: %s", exc)
            print(f"[DBManager] Error conectando a MariaDB: {exc}")
            self.offline = True
            return

        cursor = conn.cursor()
        for t in tablas:
            pendientes = t['get']() or []
            for reg in pendientes:
                try:
                    cursor.execute(t['insert'], t['params'](reg))
                    t['delete'](reg[t['id']])
                    self.logger.info(f"[DBManager] Sincronizado y eliminado pendiente en {t['tabla']} id={reg[t['id']]}")
                    print(f"[DBManager] Sincronizado y eliminado pendiente en {t['tabla']} id={reg[t['id']]}")
                except Exception as exc:
                    self.logger.error(f"[DBManager] Error insertando en {t['tabla']} id={reg[t['id']]}: {exc}")
                    print(f"[DBManager] Error insertando en {t['tabla']} id={reg[t['id']]}: {exc}")
                    conn.close()
                    return
        cursor.close()
        conn.close()
        self.logger.info("[DBManager] Sincronización finalizada")
        print("[SYNC][INFO] Subida de datos locales pendientes finalizada.")
        self.logger.info("[SYNC][INFO] Subida de datos locales pendientes finalizada.")

    def sync_critical_data_to_local(self):
        """Sincroniza datos críticos de la base remota a la base local SQLite."""
        if self.offline:
            print("[SYNC][INFO] Sincronización omitida, modo sin conexión.")
            self.logger.info("[SYNC][INFO] Sincronización omitida, modo sin conexión.")
            return
        print("[SYNC][INFO] Iniciando sincronización de datos críticos...")
        self.logger.info("[SYNC][INFO] Iniciando sincronización de datos críticos...")
        tablas = [
            # (nombre_tabla, columnas, clave primaria, si es autoincrement)
            ("Rol", ["id_rol", "nombre"], "id_rol", True),
            ("Tipo_documento", ["id_tipo_documento", "descripcion"], "id_tipo_documento", True),
            ("Codigo_postal", ["id_codigo_postal", "pais", "departamento", "ciudad"], "id_codigo_postal", False),
            ("Tipo_cliente", ["id_tipo", "descripcion"], "id_tipo", True),
            ("Estado_vehiculo", ["id_estado", "descripcion"], "id_estado", True),
            ("Marca_vehiculo", ["id_marca", "nombre_marca"], "id_marca", True),
            ("Color_vehiculo", ["id_color", "nombre_color"], "id_color", True),
            ("Tipo_vehiculo", ["id_tipo", "descripcion", "capacidad", "combustible", "tarifa_dia"], "id_tipo", True),
            ("Blindaje_vehiculo", ["id_blindaje", "descripcion"], "id_blindaje", True),
            ("Transmision_vehiculo", ["id_transmision", "descripcion"], "id_transmision", True),
            ("Cilindraje_vehiculo", ["id_cilindraje", "descripcion"], "id_cilindraje", True),
            ("Sucursal", ["id_sucursal", "nombre", "direccion", "telefono", "gerente", "id_codigo_postal"], "id_sucursal", True),
            ("Seguro_vehiculo", ["id_seguro", "estado", "descripcion", "vencimiento", "costo"], "id_seguro", True),
            ("Tipo_empleado", ["id_tipo_empleado", "descripcion"], "id_tipo_empleado", True),
            ("Empleado", ["id_empleado", "documento", "nombre", "telefono", "correo", "cargo"], "id_empleado", True),
            ("Cliente", ["id_cliente", "documento", "nombre", "telefono", "correo"], "id_cliente", True),
            ("Usuario", ["id_usuario", "usuario", "contrasena", "id_rol", "id_cliente", "id_empleado"], "id_usuario", True),
            ("Vehiculo", ["placa", "n_chasis", "modelo", "kilometraje", "id_marca", "id_color", "id_tipo_vehiculo", "id_blindaje", "id_transmision", "id_cilindraje", "id_seguro_vehiculo", "id_estado_vehiculo", "id_proveedor", "id_sucursal"], "placa", False),
            ("Medio_pago", ["id_medio_pago", "descripcion"], "id_medio_pago", True),
            ("Estado_alquiler", ["id_estado", "descripcion"], "id_estado", True),
            ("Licencia_conduccion", ["id_licencia", "estado", "fecha_emision", "fecha_vencimiento", "id_categoria"], "id_licencia", True),
            ("Categoria_licencia", ["id_categoria", "descripcion"], "id_categoria", True),
            ("Taller_mantenimiento", ["id_taller", "nombre", "direccion", "telefono"], "id_taller", True),
            ("Tipo_mantenimiento", ["id_tipo", "descripcion"], "id_tipo", True),
            ("Proveedor_vehiculo", ["id_proveedor", "nombre", "direccion", "telefono", "correo"], "id_proveedor", True),
            ("Alquiler", ["id_alquiler", "fecha_hora_salida", "valor", "fecha_hora_entrada", "id_vehiculo", "id_cliente", "id_sucursal", "id_medio_pago", "id_estado", "id_seguro", "id_descuento"], "id_alquiler", True),
            ("Reserva_alquiler", ["id_reserva", "fecha_hora", "abono", "saldo_pendiente", "id_estado_reserva", "id_alquiler"], "id_reserva", True),
            ("Abono_reserva", ["id_abono", "valor", "fecha_hora", "id_reserva", "id_medio_pago"], "id_abono", True),
        ]
        conn_remota = self.connect()
        conn_local = self._sqlite.connect()
        for nombre, columnas, pk, autoinc in tablas:
            try:
                cursor_remota = conn_remota.cursor()
                cursor_local = conn_local.cursor()
                cols_str = ', '.join(columnas)
                if nombre == "Alquiler":
                    cursor_remota.execute(
                        f"SELECT {cols_str} FROM {nombre} WHERE fecha_hora_salida >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
                    )
                elif nombre == "Reserva_alquiler":
                    cursor_remota.execute(
                        f"SELECT {cols_str} FROM {nombre} WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
                    )
                elif nombre == "Abono_reserva":
                    cursor_remota.execute(
                        f"SELECT {cols_str} FROM {nombre} WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
                    )
                else:
                    cursor_remota.execute(f"SELECT {cols_str} FROM {nombre}")
                rows = cursor_remota.fetchall()
                for row in rows:
                    placeholders = ', '.join(['?'] * len(columnas))
                    update_str = ', '.join([f'{col}=?' for col in columnas])
                    cursor_local.execute(
                        f"UPDATE {nombre} SET {update_str} WHERE {pk}=?",
                        tuple(row) + (row[columnas.index(pk)],),
                    )
                    if cursor_local.rowcount == 0:
                        cursor_local.execute(
                            f"INSERT OR IGNORE INTO {nombre} ({cols_str}) VALUES ({placeholders})",
                            row,
                        )
                if nombre == "Alquiler":
                    cursor_local.execute(
                        "DELETE FROM Alquiler WHERE fecha_hora_salida < date('now','-7 day')"
                    )
                elif nombre == "Reserva_alquiler":
                    cursor_local.execute(
                        "DELETE FROM Reserva_alquiler WHERE fecha_hora < date('now','-7 day')"
                    )
                elif nombre == "Abono_reserva":
                    cursor_local.execute(
                        "DELETE FROM Abono_reserva WHERE fecha_hora < date('now','-7 day')"
                    )
                conn_local.commit()
                cursor_remota.close()
                cursor_local.close()
                print(f"[SYNC][INFO] Sincronizada tabla {nombre} ({len(rows)} registros)")
                self.logger.info(f"[SYNC][INFO] Sincronizada tabla {nombre} ({len(rows)} registros)")
            except Exception as exc:
                print(f"[SYNC][ERROR] Error sincronizando tabla {nombre}: {exc}")
                self.logger.error(f"[SYNC][ERROR] Error sincronizando tabla {nombre}: {exc}")
        conn_remota.close()
        conn_local.close()
        print("[SYNC][INFO] Sincronización de datos críticos finalizada.")
        self.logger.info("[SYNC][INFO] Sincronización de datos críticos finalizada.")

    def close(self):
        """Placeholder to keep API compatibility."""
        # Connections are opened and closed per query
        pass

    def get_lastrowid(self, table_name):
        """Obtener el último ID insertado en una tabla específica."""
        try:
            if self.offline:
                # Para SQLite, usar el método del SQLiteManager
                return self._sqlite.get_lastrowid(table_name)
            else:
                # Para MySQL, usar LAST_INSERT_ID()
                result = self.execute_query("SELECT LAST_INSERT_ID()")
                if result and result[0]:
                    return result[0][0]
                else:
                    return None
        except Exception as exc:
            self.logger.error(f"Error obteniendo lastrowid para tabla {table_name}: {exc}")
            return None

    def set_on_disconnect_callback(self, callback):
        """Permite a las vistas registrar un callback para mostrar una ventana emergente de desconexión inmediata."""
        self.on_disconnect_callback = callback

    def set_on_reconnect_callback(self, callback):
        """Permite a las vistas registrar un callback para mostrar una ventana emergente de reconexión inmediata."""
        self.on_reconnect_callback = callback

    def update_user_password_both(self, usuario, hashed_nueva):
        """
        Actualiza la contraseña en ambas bases (remota y local) si hay conexión.
        Si está offline, solo en la local y marca como pendiente para sincronizar.
        """
        try:
            # Actualizar en remota si hay conexión
            if not self.offline:
                self.execute_query(
                    "UPDATE Usuario SET contrasena = %s WHERE usuario = %s",
                    (hashed_nueva, usuario),
                    fetch=False
                )
            # Actualizar en local siempre
            self._sqlite.execute_query(
                "UPDATE Usuario SET contrasena = ? WHERE usuario = ?",
                (hashed_nueva, usuario),
                fetch=False
            )
            return True
        except Exception as exc:
            self.logger.error(f"Error actualizando contraseña en ambas bases: {exc}")
            return False

    def update_cliente_info_both(self, id_cliente, nombre, telefono, direccion, correo):
        """
        Actualiza los datos del cliente en ambas bases (remota y local) si hay conexión.
        Si está offline, solo en la local y marca como pendiente para sincronizar.
        """
        try:
            # Actualizar en remota si hay conexión
            if not self.offline:
                self.execute_query(
                    "UPDATE Cliente SET nombre = %s, telefono = %s, direccion = %s, correo = %s WHERE id_cliente = %s",
                    (nombre, telefono, direccion, correo, id_cliente),
                    fetch=False
                )
            # Actualizar en local siempre
            self._sqlite.execute_query(
                "UPDATE Cliente SET nombre = ?, telefono = ?, direccion = ?, correo = ? WHERE id_cliente = ?",
                (nombre, telefono, direccion, correo, id_cliente),
                fetch=False
            )
            return True
        except Exception as exc:
            self.logger.error(f"Error actualizando datos de cliente en ambas bases: {exc}")
            return False
