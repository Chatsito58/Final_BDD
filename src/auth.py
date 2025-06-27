import hashlib
import logging
import time

from .config import Config


class AuthManager:
    """Gestiona autenticación y bloqueo temporal de usuarios."""

    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self.failed_attempts = {}
        self.blocked_users = {}

    def _is_blocked(self, correo):
        """Return True if user is currently blocked."""
        unblock_time = self.blocked_users.get(correo)
        if unblock_time and time.time() < unblock_time:
            return True
        if unblock_time:
            # Bloqueo expirado
            self.blocked_users.pop(correo, None)
        return False

    def login(self, correo, contrasena):
        if self._is_blocked(correo):
            self.logger.warning("Intento de acceso de usuario bloqueado: %s", correo)
            return None

        # Aplicar hash a la contraseña
        hashed_pwd = hashlib.sha256(contrasena.encode()).hexdigest()
        
        # Consultar base de datos
        is_sqlite = getattr(self.db, 'offline', False)
        
        if is_sqlite:
            # Consulta para SQLite
            query = """
            SELECT u.id_usuario, u.usuario, r.nombre as rol,
                   u.id_cliente, u.id_empleado, e.cargo
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            LEFT JOIN Empleado e ON u.id_empleado = e.id_empleado
            WHERE u.usuario = ? AND u.contrasena = ?
            """
        else:
            # Consulta para MySQL
            query = """
            SELECT u.id_usuario, u.usuario, r.nombre as rol,
                   u.id_cliente, u.id_empleado, e.cargo
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            LEFT JOIN Empleado e ON u.id_empleado = e.id_empleado
            WHERE u.usuario = %s AND u.contrasena = %s
            """
            
        result = self.db.execute_query(query, (correo, hashed_pwd))

        if result is None:
            self.logger.error("Error ejecutando consulta de login")
            raise ConnectionError("Error executing login query")

        if result and len(result) > 0:
            row = result[0]
            self.logger.info("Usuario %s autenticado correctamente", correo)
            # Resetear intentos fallidos en caso de éxito
            self.failed_attempts.pop(correo, None)
            self.blocked_users.pop(correo, None)
            return {
                'id_usuario': row[0],
                'usuario': row[1],
                'rol': row[2],
                'id_cliente': row[3],
                'id_empleado': row[4],
                'tipo_empleado': row[5]
            }
        # Credenciales incorrectas
        attempts = self.failed_attempts.get(correo, 0) + 1
        self.failed_attempts[correo] = attempts
        self.logger.warning(
            "Intento fallido %s para el usuario %s", attempts, correo
        )
        if attempts >= Config.MAX_LOGIN_ATTEMPTS:
            self.blocked_users[correo] = time.time() + Config.BLOCK_TIME
            self.failed_attempts[correo] = 0
            self.logger.error(
                "Usuario %s bloqueado temporalmente por %s segundos",
                correo,
                Config.BLOCK_TIME,
            )
        return None
