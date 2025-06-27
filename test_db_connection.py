import os
from dotenv import load_dotenv

try:
    import mysql.connector as pymysql
except Exception as e:
    print(f"No se pudo importar el conector de MySQL: {e}")
    pymysql = None

load_dotenv()

config = {
    'host': os.getenv('DB_REMOTE_HOST'),
    'user': os.getenv('DB_REMOTE_USER'),
    'password': os.getenv('DB_REMOTE_PASSWORD'),
    'database': os.getenv('DB_REMOTE_NAME'),
    'connection_timeout': 3,
    'autocommit': True,
}

print("Probando conexión a la base de datos remota...")

if pymysql is None:
    print("El driver de MySQL no está instalado. Instala 'mysql-connector-python' en tu entorno.")
    exit(1)

try:
    conn = pymysql.connect(**config)
    print("¡Conexión exitosa a la base de datos remota!")
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM Usuario LIMIT 5;")
    rows = cursor.fetchall()
    print("Usuarios encontrados:")
    for row in rows:
        print(row)
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error al conectar o consultar la base de datos remota: {e}") 