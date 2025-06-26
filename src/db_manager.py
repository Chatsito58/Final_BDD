import os
from mysql import connector
from mysql.connector import Error
from dotenv import load_dotenv


class DBManager:
    """Simple database manager for MariaDB connections."""

    def __init__(self):
        load_dotenv()
        self.config = {
            'host': os.getenv('DB_REMOTE_HOST'),
            'user': os.getenv('DB_REMOTE_USER'),
            'password': os.getenv('DB_REMOTE_PASSWORD'),
            'database': os.getenv('DB_REMOTE_NAME'),
        }
        self._connection = None

    def connect(self):
        """Establish a database connection."""
        if self._connection is None or not self._connection.is_connected():
            self._connection = connector.connect(**self.config)
        return self._connection

    def close(self):
        """Close the active connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
