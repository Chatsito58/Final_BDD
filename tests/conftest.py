import os
import sys
import hashlib
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.db_manager import DBManager as _DBManager
from src.triple_db_manager import TripleDBManager as _TripleDBManager
from src import db_manager as db_manager_module
from src import triple_db_manager as triple_module
from src.auth import AuthManager
from src.sqlite_manager import SQLiteManager


@pytest.fixture(scope="session")
def sqlite_db_path(tmp_path_factory):
    """Create a temporary SQLite database initialized with schema and data."""
    temp_dir = tmp_path_factory.mktemp("db")
    db_file = temp_dir / "test.db"
    old = os.environ.get("LOCAL_DB_PATH")
    os.environ["LOCAL_DB_PATH"] = str(db_file)
    # Initialize database using SQLiteManager which reads schema/inserts
    SQLiteManager()
    yield str(db_file)
    if old is not None:
        os.environ["LOCAL_DB_PATH"] = old
    else:
        os.environ.pop("LOCAL_DB_PATH", None)
    if db_file.exists():
        db_file.unlink()


@pytest.fixture()
def db_manager(sqlite_db_path, monkeypatch):
    """Provide DBManager configured for the temporary SQLite database."""
    monkeypatch.setenv("LOCAL_DB_PATH", sqlite_db_path)
    monkeypatch.setattr(db_manager_module, "mysql", None)
    return _DBManager()


@pytest.fixture()
def triple_db_manager(sqlite_db_path, monkeypatch):
    """Provide TripleDBManager configured for the temporary SQLite database."""
    monkeypatch.setenv("LOCAL_DB_PATH", sqlite_db_path)
    monkeypatch.setattr(triple_module, "mysql", None)
    monkeypatch.setattr(_TripleDBManager, "_start_connection_monitoring", lambda self: None)
    manager = _TripleDBManager()
    yield manager
    manager.stop_monitoring.set()


@pytest.fixture()
def auth_manager(db_manager):
    """Return an AuthManager using the temporary DBManager."""
    return AuthManager(db_manager)


@pytest.fixture()
def sample_user(db_manager):
    """Insert and return a sample user in the temporary database."""
    user = {
        "usuario": "user@example.com",
        "password": "secret",
        "id_rol": 1,
    }
    hashed = hashlib.sha256(user["password"].encode()).hexdigest()
    db_manager.execute_query(
        "INSERT INTO Usuario (usuario, contrasena, id_rol) VALUES (%s, %s, %s)",
        (user["usuario"], hashed, user["id_rol"]),
        fetch=False,
    )
    user["hashed"] = hashed
    return user
