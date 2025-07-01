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
            ('2024-06-10 09:00:00', 200000, '2024-06-11 09:00:00', 'XYZ789', 1, 4, 1, 2, 1, 2, 2)
        """
    )
    conn.commit()
    conn.close()
    return db


def test_ventas_por_sucursal(tmp_path):
    db = setup_db(tmp_path)
    rows = reports.ventas_por_sucursal(db, 6, 2024)
    assert rows == [(1, 410000.0)]


def test_ventas_por_vendedor(tmp_path):
    db = setup_db(tmp_path)
    rows = sorted(reports.ventas_por_vendedor(db, 6, 2024))
    assert rows == [(3, 210000.0), (4, 200000.0)]
