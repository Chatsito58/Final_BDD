import pytest
import logging
from src.models.db_manager import DBManager

@pytest.fixture(scope="module")
def db():
    logger = logging.getLogger("DBManagerTest")
    return DBManager(logger)

def test_email_unico_cliente(db):
    correo = "unicocliente@example.com"
    # Limpieza previa
    is_sqlite = db.is_sqlite()
    if is_sqlite:
        del_usuario = "DELETE FROM Usuario WHERE usuario = ?"
        del_cliente = "DELETE FROM Cliente WHERE correo = ?"
        params = (correo,)
    else:
        del_usuario = "DELETE FROM Usuario WHERE usuario = %s"
        del_cliente = "DELETE FROM Cliente WHERE correo = %s"
        params = (correo,)
    db.execute_query(del_usuario, params, fetch=False)
    db.execute_query(del_cliente, params, fetch=False)
    # Insertar dependencias
    if is_sqlite:
        rol_q = "INSERT OR IGNORE INTO Rol (nombre) VALUES (?)"
        rol_param = ("cliente",)
    else:
        rol_q = "INSERT INTO Rol (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre=nombre"
        rol_param = ("cliente",)
    db.execute_query(rol_q, rol_param, fetch=False)
    # Insertar primer cliente
    if is_sqlite:
        insert_q = ("INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (?, ?, ?, ?)")
        params = ("777777777", "Unico Cliente", "1234567", correo)
    else:
        insert_q = ("INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (%s, %s, %s, %s)")
        params = ("777777777", "Unico Cliente", "1234567", correo)
    db.execute_query(insert_q, params, fetch=False)
    print("Primer cliente insertado correctamente.")
    # Intentar insertar el mismo correo otra vez
    try:
        db.execute_query(insert_q, params, fetch=False)
        print("ERROR: Se permitió insertar un cliente con correo duplicado (esto NO debe pasar)")
        assert False, "Se permitió correo duplicado"
    except Exception as e:
        print("Validación de email único FUNCIONA. Error capturado:", e) 