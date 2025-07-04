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

    def verificar_correo_existe(self, correo):
        """
        Verifica si un correo existe en la tabla Usuario.
        Retorna True si existe, False si no existe.
        """
        try:
            is_sqlite = getattr(self.db, 'offline', False)
            
            if is_sqlite:
                query = "SELECT COUNT(*) FROM Usuario WHERE usuario = ?"
            else:
                query = "SELECT COUNT(*) FROM Usuario WHERE usuario = %s"
                
            result = self.db.execute_query(query, (correo,))
            
            if result and len(result) > 0:
                count = result[0][0]
                return count > 0
            return False
            
        except Exception as e:
            self.logger.error(f"Error verificando si el correo existe: {e}")
            return False

    def login(self, correo, contrasena):
        if self._is_blocked(correo):
            self.logger.warning("Intento de acceso de usuario bloqueado: %s", correo)
            return None

        # Aplicar hash a la contraseña
        hashed_pwd = hashlib.sha256(contrasena.encode()).hexdigest()
        
        # Consultar base de datos
        is_sqlite = getattr(self.db, 'offline', False)

        # Verificar si la columna id_sucursal existe en la tabla Empleado
        columna_sucursal = False
        try:
            if is_sqlite:
                res = self.db.execute_query("PRAGMA table_info(Empleado)")
                columna_sucursal = any(
                    r[1] == "id_sucursal" for r in (res or [])
                )
            else:
                check_q = (
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE table_name='Empleado' AND column_name='id_sucursal'"
                )
                res = self.db.execute_query(check_q)
                columna_sucursal = res and res[0][0] > 0
        except Exception:
            pass

        if not columna_sucursal:
            # Consulta sin la columna id_sucursal
            placeholder = '?' if is_sqlite else '%s'
            query = f"""
            SELECT u.id_usuario, u.usuario, r.nombre as rol,
                   u.id_cliente, u.id_empleado, e.cargo, NULL
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            LEFT JOIN Empleado e ON u.id_empleado = e.id_empleado
            WHERE u.usuario = {placeholder} AND u.contrasena = {placeholder}
            """
        else:
            # Consulta con la columna disponible
            placeholder = '?' if is_sqlite else '%s'
            query = f"""
            SELECT u.id_usuario, u.usuario, r.nombre as rol,
                   u.id_cliente, u.id_empleado, e.cargo, e.id_sucursal
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            LEFT JOIN Empleado e ON u.id_empleado = e.id_empleado
            WHERE u.usuario = {placeholder} AND u.contrasena = {placeholder}
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
                'tipo_empleado': row[5],
                'id_sucursal': row[6]
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

    def cambiar_contrasena(self, usuario, contrasena_actual, nueva_contrasena):
        """
        Permite cambiar la contraseña de un usuario, validando la actual y usando SHA-256.
        Devuelve True si se actualizó correctamente, o un mensaje de error si falló alguna validación.
        """
        hashed_actual = hashlib.sha256(contrasena_actual.encode()).hexdigest()
        hashed_nueva = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
        is_sqlite = getattr(self.db, 'offline', False)
        try:
            # 1. Verificar contraseña actual
            if is_sqlite:
                query = "SELECT contrasena FROM Usuario WHERE usuario = ?"
                params = (usuario,)
            else:
                query = "SELECT contrasena FROM Usuario WHERE usuario = %s"
                params = (usuario,)
            result = self.db.execute_query(query, params)
            if not result or result[0][0] != hashed_actual:
                self.logger.warning(f"Intento fallido de cambio de contraseña para {usuario}: contraseña actual incorrecta")
                return "La contraseña actual es incorrecta."
            # 2. Validar que la nueva contraseña no sea igual a la actual
            if hashed_actual == hashed_nueva:
                self.logger.warning(f"Intento fallido de cambio de contraseña para {usuario}: nueva contraseña igual a la actual")
                return "La nueva contraseña no puede ser igual a la actual."
            # 3. Actualizar la contraseña en ambas bases
            ok = self.db.update_user_password_both(usuario, hashed_nueva)
            if ok:
                self.logger.info(f"Contraseña cambiada exitosamente para {usuario} (ambas bases)")
                return True
            else:
                return "Error actualizando la contraseña en ambas bases."
        except Exception as e:
            self.logger.error(f"Error cambiando contraseña para {usuario}: {e}")
            return f"Error cambiando la contraseña: {e}"
