import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.sqlite_manager import SQLiteManager
from src.services import reports


def setup_db(tmp_path):
    os.environ["LOCAL_DB_PATH"] = str(tmp_path / "test.db")
    db = SQLiteManager()
    conn = db.connect()
    conn.execute(
        """
        INSERT INTO Alquiler (fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo,
            id_cliente, id_empleado, id_sucursal, id_medio_pago, id_estado, id_seguro, id_descuento)
        VALUES
            ('2024-06-01 10:00:00', 210000, '2024-06-03 10:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 1),
            ('2024-06-10 09:00:00', 200000, '2024-06-11 09:00:00', 'XYZ789', 1, 4, 1, 2, 1, 2, 2),
            ('2024-07-05 08:00:00', 150000, '2024-07-06 08:00:00', 'ABC123', 1, 4, 1, 1, 1, 1, 2),
            ('2024-07-12 15:00:00', 170000, '2024-07-13 15:00:00', 'XYZ789', 1, 3, 2, 2, 1, 2, 1),
            ('2024-07-20 09:00:00', 190000, '2024-07-22 09:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 2),
            ('2024-08-02 10:00:00', 250000, '2024-08-04 10:00:00', 'XYZ789', 1, 4, 2, 2, 1, 2, 1),
            ('2024-08-15 08:00:00', 230000, '2024-08-16 08:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 1)
        """
    )
    conn.execute(
        """
        INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler)
        VALUES
            ('2024-05-30 09:00:00', 100000, 110000, 1, 1),
            ('2024-06-08 08:00:00', 50000, 150000, 1, 2),
            ('2024-07-04 07:00:00', 60000, 90000, 1, 3),
            ('2024-07-11 14:00:00', 70000, 100000, 1, 4),
            ('2024-07-18 10:00:00', 90000, 100000, 1, 5),
            ('2024-08-01 12:00:00', 75000, 175000, 1, 6),
            ('2024-08-14 13:00:00', 70000, 160000, 1, 7)
        """
    )
    conn.execute(
        """
        INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago)
        VALUES
            (100000, '2024-05-30 10:00:00', 1, 1),
            (50000, '2024-06-08 09:00:00', 2, 2),
            (60000, '2024-07-04 08:00:00', 3, 1),
            (70000, '2024-07-11 15:00:00', 4, 2),
            (90000, '2024-07-18 11:00:00', 5, 1),
            (75000, '2024-08-01 13:00:00', 6, 2),
            (70000, '2024-08-14 14:00:00', 7, 1)
        """
    )
    conn.commit()
    conn.close()
    return db


def test_ventas_por_sucursal(tmp_path):
    db = setup_db(tmp_path)
    assert reports.ventas_por_sucursal(db, 6, 2024) == [(1, 410000.0)]
    rows = sorted(reports.ventas_por_sucursal(db, 7, 2024))
    assert rows == [(1, 340000.0), (2, 170000.0)]


def test_ventas_por_vendedor(tmp_path):
    db = setup_db(tmp_path)
    assert sorted(reports.ventas_por_vendedor(db, 6, 2024)) == [
        (3, 210000.0),
        (4, 200000.0),
    ]
    rows = sorted(reports.ventas_por_vendedor(db, 7, 2024))
    assert rows == [(3, 360000.0), (4, 150000.0)]


def test_ventas_mensuales(tmp_path):
    db = setup_db(tmp_path)
    rows = reports.ventas_mensuales(db, 2024)
    assert rows == [(6, 410000.0), (7, 510000.0), (8, 480000.0)]
