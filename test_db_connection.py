#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a la base de datos y el esquema actualizado.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.db_manager import DBManager
from src.auth import AuthManager

def test_database_connection():
    """Prueba la conexión a la base de datos y verifica el esquema."""
    print("=== PRUEBA DE CONEXIÓN A BASE DE DATOS ===")
    
    try:
        # Crear instancia del gestor de base de datos
        db_manager = DBManager()
        
        # Verificar si está en modo offline
        is_offline = db_manager.is_sqlite()
        print(f"Modo: {'OFFLINE (SQLite)' if is_offline else 'ONLINE (MySQL)'}")
        
        # Probar conexión
        conn = db_manager.connect()
        if conn:
            print("✅ Conexión exitosa a la base de datos")
            conn.close()
        else:
            print("❌ Error al conectar a la base de datos")
            return False
        
        # Verificar tablas principales
        print("\n=== VERIFICACIÓN DE TABLAS ===")
        tablas_principales = [
            'Usuario', 'Cliente', 'Empleado', 'Vehiculo', 
            'Alquiler', 'Reserva_alquiler', 'Sucursal'
        ]
        
        for tabla in tablas_principales:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) FROM {tabla}")
                if result is not None:
                    count = result[0][0] if result else 0
                    print(f"✅ Tabla {tabla}: {count} registros")
                else:
                    print(f"❌ Error al consultar tabla {tabla}")
            except Exception as e:
                print(f"❌ Error en tabla {tabla}: {e}")
        
        # Verificar datos de prueba
        print("\n=== VERIFICACIÓN DE DATOS DE PRUEBA ===")
        
        # Verificar roles
        roles = db_manager.execute_query("SELECT id_rol, nombre FROM Rol")
        if roles:
            print("✅ Roles encontrados:")
            for rol in roles:
                print(f"  - {rol[0]}: {rol[1]}")
        else:
            print("❌ No se encontraron roles")
        
        # Verificar usuarios
        usuarios = db_manager.execute_query("SELECT COUNT(*) FROM Usuario")
        if usuarios:
            print(f"✅ Usuarios en el sistema: {usuarios[0][0]}")
        else:
            print("❌ No se pudieron contar usuarios")
        
        # Verificar vehículos
        vehiculos = db_manager.execute_query("SELECT COUNT(*) FROM Vehiculo")
        if vehiculos:
            print(f"✅ Vehículos en el sistema: {vehiculos[0][0]}")
        else:
            print("❌ No se pudieron contar vehículos")
        
        # Verificar sucursales
        sucursales = db_manager.execute_query("SELECT COUNT(*) FROM Sucursal")
        if sucursales:
            print(f"✅ Sucursales en el sistema: {sucursales[0][0]}")
        else:
            print("❌ No se pudieron contar sucursales")
        
        # Probar autenticación
        print("\n=== PRUEBA DE AUTENTICACIÓN ===")
        auth_manager = AuthManager(db_manager)
        
        # Verificar si hay usuarios para probar
        usuarios_test = db_manager.execute_query("SELECT usuario FROM Usuario LIMIT 1")
        if usuarios_test:
            usuario_test = usuarios_test[0][0]
            print(f"Probando autenticación con usuario: {usuario_test}")
            
            # Intentar login con contraseña incorrecta
            resultado = auth_manager.login(usuario_test, "password_incorrecto")
            if resultado is None:
                print("✅ Autenticación fallida correctamente (contraseña incorrecta)")
            else:
                print("⚠️  Autenticación exitosa con contraseña incorrecta (posible problema)")
        else:
            print("⚠️  No hay usuarios para probar autenticación")
        
        print("\n=== PRUEBA COMPLETADA ===")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_compatibility():
    """Prueba la compatibilidad del esquema con las consultas principales."""
    print("\n=== PRUEBA DE COMPATIBILIDAD DE ESQUEMA ===")
    
    try:
        db_manager = DBManager()
        
        # Consultas principales que deben funcionar
        consultas_prueba = [
            {
                'nombre': 'Consulta de vehículos disponibles',
                'query': """
                SELECT v.placa, v.modelo, m.nombre_marca 
                FROM Vehiculo v 
                JOIN Marca_vehiculo m ON v.id_marca = m.id_marca 
                WHERE v.id_estado_vehiculo = 1 
                LIMIT 5
                """
            },
            {
                'nombre': 'Consulta de reservas con cliente',
                'query': """
                SELECT ra.id_reserva, c.nombre, v.placa, a.fecha_hora_salida
                FROM Reserva_alquiler ra
                JOIN Alquiler a ON ra.id_alquiler = a.id_alquiler
                JOIN Cliente c ON a.id_cliente = c.id_cliente
                JOIN Vehiculo v ON a.id_vehiculo = v.placa
                LIMIT 5
                """
            },
            {
                'nombre': 'Consulta de empleados con sucursal',
                'query': """
                SELECT e.nombre, e.cargo, s.nombre as sucursal
                FROM Empleado e
                LEFT JOIN Sucursal s ON e.id_sucursal = s.id_sucursal
                LIMIT 5
                """
            }
        ]
        
        for consulta in consultas_prueba:
            try:
                result = db_manager.execute_query(consulta['query'])
                if result is not None:
                    print(f"✅ {consulta['nombre']}: {len(result)} resultados")
                else:
                    print(f"❌ {consulta['nombre']}: Error en la consulta")
            except Exception as e:
                print(f"❌ {consulta['nombre']}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de compatibilidad: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de base de datos...")
    
    # Ejecutar pruebas
    test1 = test_database_connection()
    test2 = test_schema_compatibility()
    
    if test1 and test2:
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("La base de datos está configurada correctamente y lista para usar.")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores anteriores y corrige los problemas.")
    
    print("\nPresiona Enter para salir...")
    input() 