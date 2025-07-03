import sys
import types
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

from src.services.roles import (
    puede_gestionar_gerentes,
    verificar_permiso_creacion_empleado,
    cargos_permitidos_para_gerente,
    puede_ejecutar_sql_libre,
)

@pytest.mark.parametrize(
    "rol,expected",
    [
        ("admin", True),
        ("ADMIN", True),
        ("gerente", False),
        ("empleado", False),
        ("otro", False),
    ],
)
def test_puede_gestionar_gerentes(rol, expected):
    assert puede_gestionar_gerentes(rol) is expected

@pytest.mark.parametrize(
    "cargo,rol,expected",
    [
        (c, "admin", True) for c in ["admin", "gerente", "ventas", "caja", "mantenimiento"]
    ]
    + [
        ("admin", "gerente", False),
        ("gerente", "gerente", False),
        ("ventas", "gerente", True),
        ("caja", "gerente", True),
        ("mantenimiento", "gerente", True),
    ]
    + [
        (c, "empleado", False) for c in ["admin", "gerente", "ventas", "caja", "mantenimiento"]
    ]
)
def test_verificar_permiso_creacion_empleado(cargo, rol, expected):
    assert verificar_permiso_creacion_empleado(cargo, rol) is expected


def test_cargos_permitidos_para_gerente():
    assert cargos_permitidos_para_gerente() == ["ventas", "caja", "mantenimiento"]

@pytest.mark.parametrize(
    "rol,expected",
    [
        ("admin", True),
        ("ADMIN", True),
        ("gerente", False),
        ("empleado", False),
        ("otro", False),
    ],
)
def test_puede_ejecutar_sql_libre(rol, expected):
    assert puede_ejecutar_sql_libre(rol) is expected
