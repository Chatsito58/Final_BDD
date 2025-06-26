from mysql.connector import connect, Error
from src.config import Config

class DBManager:
    def __init__(self):
        self.config = {
            'host': Config.DB_REMOTE_HOST,
            'user': Config.DB_REMOTE_USER,
            'password': Config.DB_REMOTE_PASSWORD,
            'database': Config.DB_REMOTE_NAME
        }

    def get_connection(self):
        try:
            conn = connect(**self.config)
            return conn
        except Error as e:
            print(f"Error de conexi\u00f3n a la base de datos: {e}")
            return None

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            conn.commit()
            return result
        except Error as e:
            print(f"Error en consulta SQL: {e}")
            return None
        finally:
            conn.close()
