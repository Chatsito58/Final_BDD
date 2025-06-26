import pytest
import os
import logging
from src.models.db_manager import DBManager

@pytest.fixture(scope="module")
def db():
    # Forzar modo offline para probar SQLite
    os.environ["DB_REMOTE_HOST"] = "invalid_host"  # Forzar fallo de conexión
    logger = logging.getLogger("DBManagerTest")
    return DBManager(logger)

def test_reserva_offline(db):
    is_sqlite = db.is_sqlite()
    # Insertar cliente y vehículo de prueba en SQLite
    if is_sqlite:
        del_reserva = "DELETE FROM Reserva WHERE id_cliente = ?"
        del_cliente = "DELETE FROM Cliente WHERE id_cliente = ?"
        del_vehiculo = "DELETE FROM Vehiculo WHERE placa = ?"
        ins_cliente = "INSERT INTO Cliente (id_cliente, documento, nombre, correo) VALUES (?, ?, ?, ?)"
        ins_vehiculo = "INSERT INTO Vehiculo (placa) VALUES (?)"
        params_cliente = (1, "111111111", "Cliente Offline", "offline@example.com")
        params_vehiculo = ("TEST123",)
        params_id = (1,)
        params_placa = ("TEST123",)
    else:
        del_reserva = "DELETE FROM Reserva WHERE id_cliente = %s"
        del_cliente = "DELETE FROM Cliente WHERE id_cliente = %s"
        del_vehiculo = "DELETE FROM Vehiculo WHERE placa = %s"
        ins_cliente = "INSERT INTO Cliente (id_cliente, documento, nombre, correo) VALUES (%s, %s, %s, %s)"
        ins_vehiculo = "INSERT INTO Vehiculo (placa) VALUES (%s)"
        params_cliente = (1, "111111111", "Cliente Offline", "offline@example.com")
        params_vehiculo = ("TEST123",)
        params_id = (1,)
        params_placa = ("TEST123",)
    db.execute_query(del_reserva, params_id, fetch=False)
    db.execute_query(del_cliente, params_id, fetch=False)
    db.execute_query(del_vehiculo, params_placa, fetch=False)
    db.execute_query(ins_cliente, params_cliente, fetch=False)
    db.execute_query(ins_vehiculo, params_vehiculo, fetch=False)
    # Crear reserva en modo offline
    reserva = {
        "fecha_hora_salida": "2024-06-26 10:00:00",
        "fecha_hora_entrada": "2024-06-27 10:00:00",
        "id_vehiculo": "TEST123",
        "id_cliente": 1,
        "id_seguro": None,
        "id_estado": 1,
    }
    db.save_pending_reservation(reserva)
    pendientes = db._sqlite.get_pending_reservations()
    print("Reservas pendientes en SQLite:", pendientes)
    assert pendientes, "No se guardó la reserva en modo offline"
    print("Test de reserva offline PASÓ correctamente.") 