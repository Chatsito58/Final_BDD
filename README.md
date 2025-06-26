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
