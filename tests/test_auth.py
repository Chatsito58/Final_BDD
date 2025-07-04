from src.auth import AuthManager

class DummyDB:
    def __init__(self, offline):
        self.offline = offline
        self.calls = []

    def execute_query(self, query, params=None, fetch=True, return_lastrowid=False):
        self.calls.append(query)
        if query.startswith("PRAGMA"):
            # Simulate SQLite table_info result with id_sucursal column
            return [(0, "id_empleado", "INTEGER", 0, None, 0),
                    (1, "id_sucursal", "INTEGER", 0, None, 0)]
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            # Simulate MySQL information_schema result
            return [(1,)]
        if "FROM Usuario" in query:
            # Simulate a user row returned from login query
            return [(1, "user", "rol", None, None, None, 5)]
        return []

    # methods used in AuthManager but not needed in tests
    def update_user_password_both(self, *a, **k):
        pass


def test_login_offline_uses_pragma():
    db = DummyDB(offline=True)
    auth = AuthManager(db)
    result = auth.login("user", "password")
    assert result["id_usuario"] == 1
    assert db.calls[0].startswith("PRAGMA")
    # placeholder should be '?' so query contains '?'
    assert "?" in db.calls[1]
    assert not any("INFORMATION_SCHEMA" in c for c in db.calls)


def test_login_online_uses_information_schema():
    db = DummyDB(offline=False)
    auth = AuthManager(db)
    result = auth.login("user", "password")
    assert result["id_usuario"] == 1
    assert any("INFORMATION_SCHEMA" in c for c in db.calls)
    # placeholder should be '%s'
    assert "%s" in db.calls[1]
