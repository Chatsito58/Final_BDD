def puede_gestionar_gerentes(rol_actual):
    """Solo el admin puede crear/editar/eliminar gerentes."""
    return rol_actual.lower() == 'admin'

def verificar_permiso_creacion_empleado(cargo, rol_actual):
    """
    - Admin puede crear cualquier empleado.
    - Gerente puede crear cualquier empleado excepto gerentes y admin.
    - Otros empleados no pueden crear empleados.
    """
    cargo = cargo.lower()
    rol_actual = rol_actual.lower()
    if rol_actual == 'admin':
        return True
    if rol_actual == 'gerente' and cargo not in ('gerente', 'admin'):
        return True
    return False

def cargos_permitidos_para_gerente():
    """Lista de cargos que un gerente puede asignar al crear/editar empleados."""
    return ['ventas', 'caja', 'mantenimiento']

def puede_ejecutar_sql_libre(rol_actual):
    """Solo el admin puede ejecutar consultas SQL libres."""
    return rol_actual.lower() == 'admin' 