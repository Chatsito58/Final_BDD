import hashlib
import sqlite3
from src.auth import AuthManager

class DummyDB:
    def __init__(self, conn):
        self.conn = conn
        self.offline = False  # simulate MySQL

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            return [(0,)]
        query = query.replace('%s', '?')
        cur = self.conn.cursor()
        cur.execute(query, params or ())
        if return_lastrowid:
            last_id = cur.lastrowid
            self.conn.commit()
            cur.close()
            return last_id
        if fetch:
            result = cur.fetchall()
        else:
            self.conn.commit()
            result = None
        cur.close()
        return result


def setup_db(tmp_path):
    db_path = tmp_path / 'no_branch.db'
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE Rol(id_rol INTEGER PRIMARY KEY, nombre TEXT)")
    conn.execute("CREATE TABLE Empleado(id_empleado INTEGER PRIMARY KEY, cargo TEXT)")
    conn.execute(
        "CREATE TABLE Usuario(id_usuario INTEGER PRIMARY KEY, usuario TEXT, contrasena TEXT, id_rol INTEGER, id_cliente INTEGER, id_empleado INTEGER)"
    )
    conn.execute("INSERT INTO Rol(id_rol, nombre) VALUES (1, 'empleado')")
    pwd = hashlib.sha256(b'pass').hexdigest()
    conn.execute(
        "INSERT INTO Empleado(id_empleado, cargo) VALUES (1, 'clerk')"
    )
    conn.execute(
        "INSERT INTO Usuario(id_usuario, usuario, contrasena, id_rol, id_cliente, id_empleado)"
        " VALUES (1, 'test@example.com', ?, 1, NULL, 1)",
        (pwd,)
    )
    conn.commit()
    return conn


def test_login_without_branch_column(tmp_path):
    conn = setup_db(tmp_path)
    db = DummyDB(conn)
    auth = AuthManager(db)
    user = auth.login('test@example.com', 'pass')
    assert user['usuario'] == 'test@example.com'
    assert user['id_sucursal'] is None

