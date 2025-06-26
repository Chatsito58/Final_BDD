import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the project root .env file
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DB_REMOTE_HOST = os.getenv("DB_REMOTE_HOST")
DB_REMOTE_USER = os.getenv("DB_REMOTE_USER")
DB_REMOTE_PASSWORD = os.getenv("DB_REMOTE_PASSWORD")
DB_REMOTE_NAME = os.getenv("DB_REMOTE_NAME")

# Application constants
MAX_INTENTOS_LOGIN = 3
TIMEOUT_CONEXION = 5
RUTA_DB_LOCAL = "local.db"
