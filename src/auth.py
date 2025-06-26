import hashlib


class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def login(self, usuario, contrasena):
        # Aplicar hash a la contrase\u00f1a
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

        # Si la consulta devuelve None, hubo un problema de base de datos
        if result is None:
            raise ConnectionError("Error executing login query")

        if result and len(result) > 0:
            # Convertir resultado en diccionario
            row = result[0]
            return {
                'id_usuario': row[0],
                'usuario': row[1],
                'rol': row[2],
                'id_cliente': row[3],
                'id_empleado': row[4]
            }
        return None
