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

    def _is_blocked(self, usuario):
        """Return True if user is currently blocked."""
        unblock_time = self.blocked_users.get(usuario)
        if unblock_time and time.time() < unblock_time:
            return True
        if unblock_time:
            # Bloqueo expirado
            self.blocked_users.pop(usuario, None)
        return False

    def login(self, usuario, contrasena):
        if self._is_blocked(usuario):
            self.logger.warning("Intento de acceso de usuario bloqueado: %s", usuario)
            return None

        # Aplicar hash a la contraseña
        hashed_pwd = hashlib.sha256(contrasena.encode()).hexdigest()
        # Consultar base de datos
        query = """
        SELECT u.id_usuario, u.usuario, r.nombre as rol, 
               u.id_cliente, u.id_empleado
        FROM Usuario u
        JOIN Rol r ON u.id_rol = r.id_rol
        WHERE u.usuario = %s AND u.contrasena = %s
        """
        result = self.db.execute_query(query, (usuario, hashed_pwd))

        if result is None:
            self.logger.error("Error ejecutando consulta de login")
            raise ConnectionError("Error executing login query")

        if result and len(result) > 0:
            row = result[0]
            self.logger.info("Usuario %s autenticado correctamente", usuario)
            # Resetear intentos fallidos en caso de éxito
            self.failed_attempts.pop(usuario, None)
            self.blocked_users.pop(usuario, None)
            return {
                'id_usuario': row[0],
                'usuario': row[1],
                'rol': row[2],
                'id_cliente': row[3],
                'id_empleado': row[4]
            }
        # Credenciales incorrectas
        attempts = self.failed_attempts.get(usuario, 0) + 1
        self.failed_attempts[usuario] = attempts
        self.logger.warning(
            "Intento fallido %s para el usuario %s", attempts, usuario
        )
        if attempts >= Config.MAX_LOGIN_ATTEMPTS:
            self.blocked_users[usuario] = time.time() + Config.BLOCK_TIME
            self.failed_attempts[usuario] = 0
            self.logger.error(
                "Usuario %s bloqueado temporalmente por %s segundos",
                usuario,
                Config.BLOCK_TIME,
            )
        return None
