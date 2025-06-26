import hashlib
from mysql.connector import Error

from .db_manager import DBManager


class AuthManager:
    """Handles user authentication."""

    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DBManager()

    def login(self, usuario: str, contrasena: str):
        """Validate credentials and return user info dictionary or None."""
        password_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        query = (
            "SELECT u.id_usuario, r.nombre AS rol, u.id_cliente, u.id_empleado "
            "FROM Usuario u JOIN Rol r ON u.id_rol = r.id_rol "
            "WHERE u.usuario = %s AND u.contrasena = %s"
        )
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (usuario, password_hash))
            result = cursor.fetchone()
            cursor.close()
            return result  # Returns None if no match
        except Error as exc:
            raise ConnectionError(f"Error de conexión a la base de datos: {exc}")
