import hashlib
import sqlite3

from src.auth import AuthManager


class InMemoryDB:
    """Simple in-memory SQLite DB for auth tests."""

    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.offline = True  # make AuthManager treat as SQLite
        self._setup()

    def _setup(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE Rol(id_rol INTEGER PRIMARY KEY, nombre TEXT)")
        cur.execute(
            "CREATE TABLE Empleado(id_empleado INTEGER PRIMARY KEY, cargo TEXT, id_sucursal INTEGER)"
        )
        cur.execute(
            "CREATE TABLE Usuario(id_usuario INTEGER PRIMARY KEY, usuario TEXT, contrasena TEXT, id_rol INTEGER, id_cliente INTEGER, id_empleado INTEGER, pendiente INTEGER DEFAULT 0)"
        )
        cur.execute("INSERT INTO Rol(id_rol, nombre) VALUES (1, 'empleado')")
        cur.execute(
            "INSERT INTO Empleado(id_empleado, cargo, id_sucursal) VALUES (1, 'clerk', 1)"
        )
        pwd = hashlib.sha256(b'pass').hexdigest()
        cur.execute(
            "INSERT INTO Usuario(id_usuario, usuario, contrasena, id_rol, id_cliente, id_empleado) VALUES (1, 'user@example.com', ?, 1, NULL, 1)",
            (pwd,),
        )
        self.conn.commit()

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        # Handle schema check used in AuthManager.login
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            cur = self.conn.cursor()
            cur.execute("PRAGMA table_info(Empleado)")
            cols = [r[1] for r in cur.fetchall()]
            cur.close()
            return [(1 if 'id_sucursal' in cols else 0,)]

        if '%s' in query:
            query = query.replace('%s', '?')
        cur = self.conn.cursor()
        cur.execute(query, params or ())
        if return_lastrowid:
            last_id = cur.lastrowid
            self.conn.commit()
            cur.close()
            return last_id
        if fetch:
            rows = cur.fetchall()
        else:
            self.conn.commit()
            rows = None
        cur.close()
        return rows

    def update_user_password_both(self, usuario, hashed_nueva):
        self.conn.execute(
            "UPDATE Usuario SET contrasena=?, pendiente=0 WHERE usuario=?",
            (hashed_nueva, usuario),
        )
        self.conn.commit()
        return True


def test_login_block_after_three_attempts():
    db = InMemoryDB()
    auth = AuthManager(db)

    for _ in range(3):
        assert auth.login('user@example.com', 'wrong') is None

    assert auth.login('user@example.com', 'pass') is None
    assert 'user@example.com' in auth.blocked_users


def test_cambiar_contrasena_success():
    db = InMemoryDB()
    auth = AuthManager(db)

    result = auth.cambiar_contrasena('user@example.com', 'pass', 'newpass')
    assert result is True
    row = db.execute_query(
        'SELECT contrasena FROM Usuario WHERE usuario = ?',
        ('user@example.com',)
    )
    assert row[0][0] == hashlib.sha256(b'newpass').hexdigest()


def test_cambiar_contrasena_fail_wrong_current():
    db = InMemoryDB()
    auth = AuthManager(db)

    result = auth.cambiar_contrasena('user@example.com', 'badpass', 'newpass')
    assert result == 'La contraseña actual es incorrecta.'


def test_verificar_correo_existe():
    db = InMemoryDB()
    auth = AuthManager(db)

    assert auth.verificar_correo_existe('user@example.com') is True
    assert auth.verificar_correo_existe('otro@example.com') is False
