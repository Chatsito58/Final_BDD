import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuraci\u00f3n de base de datos
    DB_REMOTE_HOST = os.getenv('DB_REMOTE_HOST', 'localhost')
    DB_REMOTE_USER = os.getenv('DB_REMOTE_USER', 'root')
    DB_REMOTE_PASSWORD = os.getenv('DB_REMOTE_PASSWORD', '')
    DB_REMOTE_NAME = os.getenv('DB_REMOTE_NAME', 'Alquiler_vehiculos')

    # Configuraci\u00f3n de seguridad
    MAX_LOGIN_ATTEMPTS = 3
    # Tiempo de bloqueo en segundos cuando se supera el número de intentos
    BLOCK_TIME = 600  # 10 minutos
    PASSWORD_HASH = "sha256"
