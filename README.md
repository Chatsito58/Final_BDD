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
