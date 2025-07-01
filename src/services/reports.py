"""Simple reporting utilities for sales aggregated from ``Alquiler``."""

from typing import List, Tuple, Any

from ..sqlite_manager import SQLiteManager


def _is_sqlite(db) -> bool:
    """Determine if a db manager works with SQLite."""
    if isinstance(db, SQLiteManager):
        return True
    if hasattr(db, "is_sqlite"):
        try:
            return db.is_sqlite()
        except Exception:
            pass
    return getattr(db, "offline", False)


def ventas_por_sucursal(db, mes: int, anio: int) -> List[Tuple[Any, float]]:
    """Return total sales grouped by branch for a given month."""
    if _is_sqlite(db):
        query = (
            "SELECT id_sucursal, SUM(valor) as total "
            "FROM Alquiler "
            "WHERE strftime('%m', fecha_hora_salida) = ? "
            "AND strftime('%Y', fecha_hora_salida) = ? "
            "GROUP BY id_sucursal"
        )
        params = (f"{mes:02d}", str(anio))
    else:
        query = (
            "SELECT id_sucursal, SUM(valor) as total "
            "FROM Alquiler "
            "WHERE MONTH(fecha_hora_salida) = %s "
            "AND YEAR(fecha_hora_salida) = %s "
            "GROUP BY id_sucursal"
        )
        params = (mes, anio)
    return db.execute_query(query, params) or []


def ventas_por_vendedor(db, mes: int, anio: int) -> List[Tuple[Any, float]]:
    """Return total sales grouped by employee for a given month."""
    if _is_sqlite(db):
        query = (
            "SELECT id_empleado, SUM(valor) as total "
            "FROM Alquiler "
            "WHERE strftime('%m', fecha_hora_salida) = ? "
            "AND strftime('%Y', fecha_hora_salida) = ? "
            "GROUP BY id_empleado"
        )
        params = (f"{mes:02d}", str(anio))
    else:
        query = (
            "SELECT id_empleado, SUM(valor) as total "
            "FROM Alquiler "
            "WHERE MONTH(fecha_hora_salida) = %s "
            "AND YEAR(fecha_hora_salida) = %s "
            "GROUP BY id_empleado"
        )
        params = (mes, anio)
    return db.execute_query(query, params) or []


def ventas_mensuales(db, anio: int) -> List[Tuple[int, float]]:
    """Return total sales per month of a given year."""
    if _is_sqlite(db):
        query = (
            "SELECT CAST(strftime('%m', fecha_hora_salida) AS INTEGER) as mes, "
            "SUM(valor) as total "
            "FROM Alquiler "
            "WHERE strftime('%Y', fecha_hora_salida) = ? "
            "GROUP BY mes ORDER BY mes"
        )
        params = (anio,)
    else:
        query = (
            "SELECT MONTH(fecha_hora_salida) as mes, SUM(valor) as total "
            "FROM Alquiler "
            "WHERE YEAR(fecha_hora_salida) = %s "
            "GROUP BY mes ORDER BY mes"
        )
        params = (anio,)
    return db.execute_query(query, params) or []
