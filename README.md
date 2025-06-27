# Final_BDD

This repository contains SQL scripts and basic configuration files for a car rental system.

The `data/sql_bases-2.sql` script defines the database schema for MariaDB, including tables for roles and users linked to existing entities.

## Redundant database mode

`DBManager` now works as a router. It first tries to connect to the remote
MariaDB instance using the variables defined in `.env`. If that connection
fails the manager automatically falls back to a local SQLite database defined by
`LOCAL_DB_PATH`. When SQLite is in use the attribute `offline` of `DBManager`
will be set to `True` and all subsequent queries are executed on the local
file. This allows the application to keep basic functionality when the remote
server is unreachable.

## Local offline storage

When the application cannot reach the remote MariaDB server, reservations are now stored in the local SQLite database. The schema for this lightweight database lives in `data/sqlite_schema.sql` and creates the tables `Cliente`, `Reserva` and `Abono`. Each table includes a `pendiente` column used to mark records that still need to be synchronized with the remote server.

## Sincronización automática

`DBManager.sync_pending_reservations()` revisa periódicamente los registros
pendientes en la base de datos local e intenta insertarlos en MariaDB. Cuando la
operación tiene éxito dichos registros se eliminan de SQLite. Este proceso se
ejecuta cada cinco minutos desde `MainView` usando un `QTimer`.

## Ejemplo de configuración de logs

El proyecto utiliza el módulo `logging` para registrar accesos, errores y
eventos de sincronización. Una configuración básica podría colocarse al inicio
de la aplicación:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)
```

Esto generará un archivo `app.log` con los eventos producidos por
`AuthManager` y `DBManager`, además de mostrarlos por consola.

## Triggers automáticos de usuario

Tanto en la base de datos remota (MariaDB/MySQL) como en la local (SQLite), existen triggers que crean automáticamente un registro en la tabla `Usuario` cada vez que se inserta un nuevo `Cliente` o `Empleado`:

- Al registrar un **Cliente**, se crea un usuario con rol 'cliente'.
- Al registrar un **Empleado**, se crea un usuario con rol 'empleado'.

Esto asegura que cada persona registrada pueda autenticarse según su rol.

## Validación de email único

El sistema valida que el correo electrónico de cada cliente sea único antes de permitir el registro, tanto en modo remoto como local. Si el correo ya existe, el registro es rechazado y se muestra un mensaje de error.

## Autenticación por correo

El inicio de sesión ahora utiliza la dirección de correo almacenada en la tabla
`Usuario`. El sistema valida la contraseña cifrada con SHA-256 y registra en el
archivo de logs cada intento exitoso o fallido. Tras **tres** intentos fallidos
consecutivos el usuario será bloqueado durante diez minutos. El modo offline se
maneja de forma automática a través de `DBManager` y su respaldo en SQLite.

## Cómo comprobar que todo funciona

### Prueba manual

1. **Registro de Cliente**
   - Intenta registrar un cliente con un correo nuevo: debe crearse el cliente y el usuario asociado.
   - Intenta registrar otro cliente con el mismo correo: debe mostrar un error de "correo ya registrado".
   - Verifica en la tabla `Usuario` que se haya creado el usuario con el rol correcto.

2. **Registro de Empleado**
   - Inserta un empleado (puedes hacerlo desde la app o directamente en la base de datos).
   - Verifica que se crea automáticamente un usuario asociado en la tabla `Usuario` con el rol 'empleado'.

3. **Modo offline**
   - Desconecta la base remota y registra un cliente: debe guardarse en SQLite y sincronizarse cuando vuelva la conexión.

4. **Triggers**
   - Inserta un cliente o empleado directamente en la base de datos y verifica que se crea el usuario automáticamente.

### Prueba automática (sugerencia)

Puedes crear un script de test en Python usando `pytest` o `unittest` que:
- Inserte un cliente y verifique la existencia del usuario asociado.
- Inserte un empleado y verifique la existencia del usuario asociado.
- Intente registrar dos clientes con el mismo correo y verifique que el segundo es rechazado.

Ejemplo básico:
```python
# test_registro.py
import pytest
from src.db_manager import DBManager

def test_registro_cliente():
    db = DBManager()
    correo = "test@example.com"
    # Limpieza previa
    db.execute_query("DELETE FROM Usuario WHERE usuario = %s", (correo,), fetch=False)
    db.execute_query("DELETE FROM Cliente WHERE correo = %s", (correo,), fetch=False)
    # Registro
    db.execute_query("INSERT INTO Cliente (documento, nombre, telefono, correo) VALUES (%s, %s, %s, %s)", ("123", "Test", "555", correo), fetch=False)
    usuarios = db.execute_query("SELECT * FROM Usuario WHERE usuario = %s", (correo,))
    assert usuarios, "No se creó el usuario automáticamente"
```

Puedes adaptar este ejemplo para empleados y para SQLite cambiando los placeholders a `?`.

## Estructura de carpetas sugerida

- src/models/: lógica de acceso a datos y modelos (db_manager.py, sqlite_manager.py, db.py)
- src/services/: lógica de negocio y utilidades (auth.py, config.py)
- src/views/: vistas y controladores de interfaz
- tests/: tests automáticos
- data/: scripts SQL y datos de ejemplo
- ui/: archivos de interfaz gráfica

## Logging centralizado

El logging está centralizado en el archivo `main.py` y todos los logs importantes (errores, advertencias, info) se guardan en `app.log` y se muestran en consola. Se agregaron advertencias para operaciones críticas como fallos de conexión o errores de consulta.

## Test de reservas y modo offline

Hay un test automático en `tests/test_reserva_offline.py` que:
- Fuerza el modo offline (SQLite).
- Inserta un cliente y un vehículo de prueba.
- Crea una reserva en modo offline y verifica que queda pendiente en SQLite.
- Imprime las reservas pendientes para comprobación manual.

Puedes ejecutarlo con:
```bash
pytest tests/test_reserva_offline.py
```

## ¿Cómo funcionan la redundancia y la fragmentación en este proyecto?

### Redundancia (¡Siempre hay un respaldo!)

El sistema guarda los datos en dos lugares:
- **Base de datos remota (MariaDB/MySQL):** Es la principal, donde normalmente se guardan todos los datos.
- **Base de datos local (SQLite):** Es una copia de respaldo. Si la base remota falla o no hay internet, el sistema automáticamente guarda los datos aquí.

**¿Qué significa esto?**
- Si se va la conexión, ¡no pierdes nada! Todo lo que hagas se guarda localmente y luego se sincroniza cuando vuelva la conexión.
- Así, siempre hay un respaldo de tus datos y el sistema nunca se detiene.

### Fragmentación (¡Puedes trabajar aunque falte una parte!)

A veces, los datos están "fragmentados" (divididos):
- Cuando trabajas sin conexión, los datos nuevos (por ejemplo, una reserva) solo existen en la base local.
- Cuando vuelve la conexión, esos datos se envían a la base remota y se juntan con el resto.

**¿Qué significa esto?**
- Puedes seguir trabajando aunque solo tengas una parte de los datos (los locales).
- Cuando todo vuelve a la normalidad, el sistema une los datos locales con los globales automáticamente.

**Ejemplo sencillo:**
- Haces una reserva sin internet → se guarda en tu compu.
- Vuelve el internet → el sistema manda esa reserva a la base principal y la borra de la local.

Así, el sistema es robusto, no se cae y siempre puedes seguir trabajando, tengas o no conexión.

## Problema conocido: PyQt5 y conexión remota MySQL/MariaDB

### Descripción del problema

Si se importa PyQt5 (o cualquier módulo que dependa de él) **antes** de realizar la conexión remota a la base de datos con `mysql-connector-python`, la aplicación puede quedarse colgada (sin error) al intentar conectar, especialmente en Windows.

Este bug ocurre por cómo PyQt5 inicializa internamente los sockets/hilos, interfiriendo con el stack de red de Python y el conector MySQL.

### Solución implementada

- En `main.py`, la conexión remota a la base de datos se prueba **antes** de importar PyQt5 y los módulos que dependen de él.
- Si la conexión es exitosa, se importa PyQt5 y la app continúa normalmente.
- Si la conexión falla, se muestra el error y el programa termina.

#### Ejemplo de la solución:

```python
# main.py (fragmento relevante)
import os
import sys
import logging
from dotenv import load_dotenv

# Configuración de logging...

# Probar conexión remota antes de importar PyQt5
try:
    import mysql.connector
    load_dotenv()
    config = { ... }
    conn = mysql.connector.connect(**config)
    # ...
except Exception as e:
    print(f"Error de conexión: {e}")
    sys.exit(1)

# Ahora sí, importar PyQt5 y módulos de la app
from PyQt5.QtWidgets import QApplication, ...
# ...
```

**Esta solución garantiza que la app no se cuelgue y la conexión remota funcione correctamente en todos los entornos.**

## Cambios y mejoras recientes (2024)

### Sincronización automática de datos críticos
- Al iniciar la app y cada vez que se recupera la conexión, se sincronizan automáticamente todas las tablas críticas (usuarios, clientes, empleados, vehículos, catálogos, etc.) de la base remota a la local (SQLite), permitiendo operar completamente offline.
- El archivo `data/sqlite_schema.sql` fue ampliado para incluir todas las tablas necesarias para el funcionamiento offline.

### Login y operación offline robustos
- El login y las operaciones críticas funcionan en modo offline siempre que haya habido al menos una sincronización previa.
- Los datos de usuarios, clientes, vehículos y catálogos se mantienen actualizados localmente para permitir login, reservas y gestión sin conexión.

### Indicador visual de estado de conexión
- Todas las vistas principales (login, MainView, CustomTkinter) muestran un indicador 🟢/🔴 que se actualiza automáticamente cada 2 segundos, informando si la app está online u offline.

### Avisos automáticos de desconexión y reconexión
- Cuando ocurre una desconexión del servidor, aparece una ventana emergente amigable informando al usuario y cambiando a modo offline.
- Al reconectarse, aparece un aviso de que la conexión regresó y se sincronizan los cambios hechos offline.
- Estos avisos funcionan en todas las vistas principales, no solo en el login.

### Interfaz moderna y consistente
- El login y las vistas PyQt5 ahora tienen un estilo oscuro y moderno, similar a CustomTkinter, que se mantiene incluso tras cerrar sesión y volver a abrir el login.
- Se eliminaron estilos individuales de widgets para asegurar consistencia visual.

### Navegación y flujo de ventanas mejorados
- Al abrir una nueva ventana (por ejemplo, tras login o registro), la anterior se oculta o cierra correctamente, evitando múltiples ventanas abiertas o cierres inesperados.
- El botón "Volver" en el registro de cliente ya no destruye la ventana ni cierra la app, solo la oculta y regresa al login de forma segura.

### Cambio de contraseña para todos los usuarios
- Se añadió una pestaña dedicada "Cambiar contraseña" en todas las vistas principales (PyQt5 y CustomTkinter), accesible para todos los roles.
- El usuario puede cambiar su contraseña validando la actual y la nueva (con SHA-256), tanto en modo online como offline.
- Se muestran mensajes claros de éxito o error y se registran los intentos en el log.

### Logging y mensajes para desarrollador
- Se agregaron mensajes claros por consola y en el log para eventos importantes: sincronización, desconexión, reconexión, subida de datos locales, errores, etc.
- Esto facilita el monitoreo y la depuración del sistema en tiempo real.

### Otros detalles
- Se documentó el problema crítico de cuelgue por importar PyQt5 antes de conectar a la base remota y su solución.
- Se mejoró la modularidad y la experiencia visual en todos los roles y vistas.
