import os
from dotenv import load_dotenv

load_dotenv()

DB_REMOTE_HOST = os.getenv("DB_REMOTE_HOST")
DB_REMOTE_USER = os.getenv("DB_REMOTE_USER")
DB_REMOTE_PASSWORD = os.getenv("DB_REMOTE_PASSWORD")
DB_REMOTE_NAME = os.getenv("DB_REMOTE_NAME")
