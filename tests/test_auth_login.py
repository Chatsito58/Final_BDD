import hashlib
import pytest


# Helper to insert sample users

def insert_sample_users(db):
    """Insert predefined users from README for all roles."""
    # Map role names to ids in Rol table
    role_ids = {}
    for name in ["admin", "gerente", "empleado", "cliente"]:
        res = db.execute_query("SELECT id_rol FROM Rol WHERE nombre=%s", (name,))
        role_ids[name] = res[0][0]

    users = [
        ("admin", "admin123", "admin", None),
        ("gerente1", "gerente123", "gerente", None),
        ("ventas1", "ventas123", "empleado", "ventas"),
        ("caja1", "caja123", "empleado", "caja"),
        ("mantenimiento1", "mantenimiento123", "empleado", "mantenimiento"),
        ("cliente1", "cliente123", "cliente", None),
    ]

    for username, pwd, role, cargo in users:
        exists = db.execute_query(
            "SELECT COUNT(*) FROM Usuario WHERE usuario=%s", (username,)
        )[0][0]
        if exists:
            continue
        emp_id = None
        if cargo:
            emp_id = db.execute_query(
                "INSERT INTO Empleado (documento, nombre, salario, cargo, telefono, direccion, correo, id_sucursal, id_tipo_documento, id_tipo_empleado) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    f"doc_{username}",
                    f"{username}",
                    0,
                    cargo,
                    "",
                    "",
                    f"{username}@example.com",
                    1,
                    1,
                    3,
                ),
                fetch=False,
                return_lastrowid=True,
            )
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        db.execute_query(
            "INSERT INTO Usuario (usuario, contrasena, id_rol, id_empleado) VALUES (%s, %s, %s, %s)",
            (username, hashed, role_ids[role], emp_id),
            fetch=False,
        )



def test_successful_logins(auth_manager, db_manager):
    insert_sample_users(db_manager)
    creds = [
        ("admin", "admin123", "admin", None),
        ("gerente1", "gerente123", "gerente", None),
        ("ventas1", "ventas123", "empleado", "ventas"),
        ("caja1", "caja123", "empleado", "caja"),
        ("mantenimiento1", "mantenimiento123", "empleado", "mantenimiento"),
        ("cliente1", "cliente123", "cliente", None),
    ]

    for usuario, pwd, rol, _ in creds:
        result = auth_manager.login(usuario, pwd)
        assert result is not None, f"Login failed for {usuario}"
        assert result["usuario"] == usuario
        assert result["rol"] == rol


def test_login_unregistered_email(auth_manager):
    assert auth_manager.login("nouser@example.com", "pwd") is None


def test_block_after_three_failed_attempts(auth_manager, db_manager):
    insert_sample_users(db_manager)
    for _ in range(3):
        assert auth_manager.login("admin", "wrong") is None
    assert auth_manager.login("admin", "wrong") is None
    assert auth_manager._is_blocked("admin") is True


def test_verificar_correo_existe(auth_manager, db_manager):
    insert_sample_users(db_manager)
    assert auth_manager.verificar_correo_existe("admin") is True
    assert auth_manager.verificar_correo_existe("nonexistent") is False
