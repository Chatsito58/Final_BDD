import os
from mysql.connector import connect, Error
from dotenv import load_dotenv
from src.config import Config

class DatabaseHelper:
    def __init__(self):
        load_dotenv()
        self.config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
        }


    def connect(self):
        try:
            conn = connect(**self.config)
            return conn
        except Error as e:
            print(f"Error de conexi\u00f3n a la base de datos: {e}")
            return None

    def execute_query(self, query, params=None):
        conn = self.connect()
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
