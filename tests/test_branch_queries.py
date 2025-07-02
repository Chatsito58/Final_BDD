import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.db_manager import DBManager


class MockEmployee:
    def __init__(self, branch_id):
        self.id_sucursal = branch_id


def setup_branch_db(tmp_path):
    os.environ['LOCAL_DB_PATH'] = str(tmp_path / 'branch.db')
    db = DBManager()
    conn = db._sqlite.connect()
    conn.execute("INSERT INTO Sucursal (id_sucursal, nombre) VALUES (1, 'Norte')")
    conn.execute("INSERT INTO Sucursal (id_sucursal, nombre) VALUES (2, 'Sur')")
    conn.execute(
        """
        INSERT INTO Alquiler (
            fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo,
            id_cliente, id_empleado, id_sucursal, id_medio_pago,
            id_estado, id_seguro, id_descuento
        ) VALUES ('2024-06-01', 100000, '2024-06-02', 'AAA', 1, 1, 1, 1, 1, 1, 1)
        """
    )
    conn.execute(
        """
        INSERT INTO Alquiler (
            fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo,
            id_cliente, id_empleado, id_sucursal, id_medio_pago,
            id_estado, id_seguro, id_descuento
        ) VALUES ('2024-06-03', 200000, '2024-06-04', 'BBB', 2, 2, 2, 1, 1, 1, 1)
        """
    )
    conn.commit()
    conn.close()
    return db


def test_employee_queries_only_own_branch(tmp_path):
    db = setup_branch_db(tmp_path)
    query = "SELECT id_sucursal FROM Alquiler WHERE id_sucursal = %s"

    emp1 = MockEmployee(1)
    rows1 = db.execute_query(query, (emp1.id_sucursal,))
    assert rows1 == [(1,)]

    emp2 = MockEmployee(2)
    rows2 = db.execute_query(query, (emp2.id_sucursal,))
    assert rows2 == [(2,)]
