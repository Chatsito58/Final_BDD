import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración de base de datos
    DB_REMOTE_HOST = os.getenv('DB_REMOTE_HOST')
    DB_REMOTE_USER = os.getenv('DB_REMOTE_USER')
    DB_REMOTE_PASSWORD = os.getenv('DB_REMOTE_PASSWORD')
    DB_REMOTE_NAME = os.getenv('DB_REMOTE_NAME')
    DB_REMOTE_HOST2 = os.getenv('DB_REMOTE_HOST2')
    DB_REMOTE_PORT2 = os.getenv('DB_REMOTE_PORT2')
    DB_REMOTE_USER2 = os.getenv('DB_REMOTE_USER2')
    DB_REMOTE_PASSWORD2 = os.getenv('DB_REMOTE_PASSWORD2')
    DB_REMOTE_NAME2 = os.getenv('DB_REMOTE_NAME2')

    # Configuración de seguridad
    MAX_LOGIN_ATTEMPTS = 3
    # Tiempo de bloqueo en segundos cuando se supera el número de intentos
    BLOCK_TIME = 600  # 10 minutos
    PASSWORD_HASH = "sha256"
