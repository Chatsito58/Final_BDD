import pytest
import logging
from src.models.db_manager import DBManager

@pytest.fixture(scope="module")
def db():
    logger = logging.getLogger("DBManagerTest")
    return DBManager(logger)

def test_trigger_cliente_usuario(db):
    correo = "triggercliente@example.com"
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
    # Insertar cliente
    if is_sqlite:
        insert_q = ("INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (?, ?, ?, ?)")
        params = ("888888888", "Test Cliente Trigger", "1234567", correo)
        select_q = "SELECT * FROM Usuario WHERE usuario = ?"
    else:
        insert_q = ("INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (%s, %s, %s, %s)")
        params = ("888888888", "Test Cliente Trigger", "1234567", correo)
        select_q = "SELECT * FROM Usuario WHERE usuario = %s"
    db.execute_query(insert_q, params, fetch=False)
    usuarios = db.execute_query(select_q, (correo,))
    print(f"Usuarios encontrados para '{correo}':", usuarios)
    assert usuarios, "No se creó el usuario automáticamente para el cliente trigger"
    print("Test de trigger cliente->usuario PASÓ correctamente.") 