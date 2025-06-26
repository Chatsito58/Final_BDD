import pytest
import logging
from src.models.db_manager import DBManager

@pytest.fixture(scope="module")
def db():
    logger = logging.getLogger("DBManagerTest")
    return DBManager(logger)

def test_trigger_empleado_usuario(db):
    correo = "triggerempleado@example.com"
    # Limpieza previa
    is_sqlite = db.is_sqlite()
    if is_sqlite:
        del_usuario = "DELETE FROM Usuario WHERE usuario = ?"
        del_empleado = "DELETE FROM Empleado WHERE correo = ?"
        params = (correo,)
    else:
        del_usuario = "DELETE FROM Usuario WHERE usuario = %s"
        del_empleado = "DELETE FROM Empleado WHERE correo = %s"
        params = (correo,)
    db.execute_query(del_usuario, params, fetch=False)
    db.execute_query(del_empleado, params, fetch=False)
    # Insertar dependencias
    if is_sqlite:
        tipo_doc_q = "INSERT OR IGNORE INTO Tipo_documento (descripcion) VALUES (?)"
        tipo_doc_param = ("CC",)
        rol_q = "INSERT OR IGNORE INTO Rol (nombre) VALUES (?)"
        rol_param = ("empleado",)
    else:
        tipo_doc_q = "INSERT INTO Tipo_documento (descripcion) VALUES (%s) ON DUPLICATE KEY UPDATE descripcion=descripcion"
        tipo_doc_param = ("CC",)
        rol_q = "INSERT INTO Rol (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre=nombre"
        rol_param = ("empleado",)
    db.execute_query(tipo_doc_q, tipo_doc_param, fetch=False)
    db.execute_query(rol_q, rol_param, fetch=False)
    # Insertar empleado
    if is_sqlite:
        insert_q = ("INSERT INTO Empleado (documento, nombre, telefono, correo) VALUES (?, ?, ?, ?)")
        params = ("999999999", "Test Empleado Trigger", "1234567", correo)
        select_q = "SELECT * FROM Usuario WHERE usuario = ?"
    else:
        insert_q = ("INSERT INTO Empleado (documento, nombre, salario, cargo, telefono, direccion, correo, id_tipo_documento) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, (SELECT id_tipo_documento FROM Tipo_documento WHERE descripcion='CC'))")
        params = ("999999999", "Test Empleado Trigger", 2000.00, "Auxiliar", "1234567", "Calle 1", correo)
        select_q = "SELECT * FROM Usuario WHERE usuario = %s"
    db.execute_query(insert_q, params, fetch=False)
    usuarios = db.execute_query(select_q, (correo,))
    print(f"Usuarios encontrados para '{correo}':", usuarios)
    assert usuarios, "No se creó el usuario automáticamente para el empleado trigger"
    print("Test de trigger empleado->usuario PASÓ correctamente.") 