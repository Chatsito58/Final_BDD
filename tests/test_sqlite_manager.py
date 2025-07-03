import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.sqlite_manager import SQLiteManager


def setup_db(tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'local.db')
    return SQLiteManager()


def test_pending_reservation_crud(tmp_path):
    db = setup_db(tmp_path)
    db.save_pending_reservation({
        'fecha_hora_salida': '2024-06-01 10:00:00',
        'fecha_hora_entrada': '2024-06-02 10:00:00',
        'id_vehiculo': 'AAA111',
        'id_cliente': 1,
        'id_seguro': 1,
        'id_estado': 1,
    })
    rows = db.get_pending_reservations()
    assert len(rows) == 1
    rid = rows[0][0]

    db.delete_reservation(rid)
    assert db.get_pending_reservations() == []


def test_pending_abono_crud(tmp_path):
    db = setup_db(tmp_path)
    conn = db.connect()
    conn.execute(
        "INSERT INTO Abono(valor, fecha_hora, id_reserva, pendiente) VALUES (100, '2024-06-01', 1, 1)"
    )
    conn.commit()
    conn.close()

    rows = db.get_pending_abonos()
    assert len(rows) == 1
    aid = rows[0][0]
    db.delete_abono(aid)
    assert db.get_pending_abonos() == []


def test_pending_password_update(tmp_path):
    db = setup_db(tmp_path)
    conn = db.connect()
    conn.execute(
        "INSERT INTO Usuario(usuario, contrasena, pendiente) VALUES ('user', 'pwd', 1)"
    )
    conn.commit()
    conn.close()

    assert db.get_pending_password_updates() == [('user', 'pwd')]
    db.clear_pending_password('user')
    assert db.get_pending_password_updates() == []
