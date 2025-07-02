# Sistema de Alquiler de Vehículos

Este proyecto implementa una aplicación de alquiler de vehículos con una interfaz gráfica moderna y un sistema de bases de datos redundante. Funciona tanto con MySQL/MariaDB como con SQLite para ofrecer un modo offline con sincronización automática.

## Tabla de Contenidos
1. [Características principales](#caracteristicas-principales)
2. [Tecnologías utilizadas](#tecnologias-utilizadas)
3. [Requisitos](#requisitos)
4. [Instalación](#instalacion)
5. [Configuración de la base de datos](#configuracion-de-la-base-de-datos)
6. [Ejecución de la aplicación](#ejecucion-de-la-aplicacion)
7. [Usuarios de prueba](#usuarios-de-prueba)
8. [Estructura del proyecto](#estructura-del-proyecto)
9. [Modo offline y sincronización](#modo-offline-y-sincronizacion)
10. [Roles y permisos](#roles-y-permisos)
11. [Sistema de autenticación](#sistema-de-autenticacion)
12. [Sistema de abonos](#sistema-de-abonos)
13. [Logging](#logging)
14. [Ejecutar pruebas](#ejecutar-pruebas)
15. [Contribuir](#contribuir)
16. [Licencia](#licencia)
17. [Desarrolladores y soporte](#desarrolladores-y-soporte)

## Características Principales
- Interfaz gráfica moderna basada en **PyQt5** y **CustomTkinter**.
- Sistema de autenticación con roles y permisos.
- Base de datos redundante (MariaDB/MySQL como principal y SQLite en local).
- Modo offline automático con sincronización de datos cuando vuelve la conexión.
- Gestión completa de clientes, empleados, vehículos, reservas y pagos.
- Sistema de abonos que valida el primer pago mínimo del 30 % y admite múltiples abonos.
- Panel de reportes de ventas por sede y por vendedor.
- Reconexión automática con la base de datos remota cuando se restablece la red.
- Mantenimiento predictivo que sugiere cuándo programar revisiones de vehículos.

## Tecnologías Utilizadas
- **Python 3.8+**
- **PyQt5** y **CustomTkinter** para la interfaz.
- **mysql-connector-python** y **sqlite3** para la capa de datos.
- **python-dotenv** para la configuración.
- **tkcalendar** y **ttkbootstrap** como componentes adicionales de la UI.
- **pytest** para las pruebas unitarias.

## Requisitos
- Python 3.8 o superior.
- Opcional: servidor MySQL/MariaDB (para modo online).
- Conexión a internet para la sincronización inicial de datos.

## Instalación
1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd Final_BDD
   ```
2. **Crear un entorno virtual**
   ```bash
   python -m venv venv
   # Activar en Windows
   venv\Scripts\activate
   # o en Linux/macOS
   source venv/bin/activate
   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
4. **Copiar el archivo de entorno**
   ```bash
   cp .env.example .env
   ```
   Edita `.env` si deseas conectar con MySQL/MariaDB.

## Configuración de la Base de Datos
El archivo `.env` permite definir los parámetros de conexión:

| Variable            | Descripción                           | Valor por defecto       |
|---------------------|---------------------------------------|-------------------------|
| `DB_REMOTE_HOST`    | Servidor de base de datos remota      | `localhost`             |
| `DB_REMOTE_PORT`    | Puerto del servidor                   | `3306`                  |
| `DB_REMOTE_USER`    | Usuario de la base de datos           | `root`                  |
| `DB_REMOTE_PASSWORD`| Contraseña del usuario                | (vacío)                 |
| `DB_REMOTE_NAME`    | Nombre de la base de datos            | `alquiler_vehiculos`    |
| `LOCAL_DB_PATH`     | Ruta al archivo SQLite local          | `data/local.sqlite`     |

Si no dispones de MySQL/MariaDB la aplicación funcionará automáticamente en modo offline usando solo SQLite.

Los esquemas se encuentran en `data/sql_bases.sql` (MySQL) y `data/sqlite_schema.sql` (SQLite). El archivo `data/inserts_prueba.sql` contiene datos de ejemplo para pruebas.

## Ejecución de la Aplicación
Una vez instaladas las dependencias y configuradas las variables de entorno, ejecuta:
```bash
python main.py
```
Se abrirá la ventana de inicio de sesión. Según las credenciales utilizadas se mostrará la vista correspondiente al rol del usuario.

## Usuarios de Prueba
El proyecto incluye usuarios de ejemplo para cada rol:

| Usuario           | Contraseña      | Rol                       |
|-------------------|-----------------|---------------------------|
| `admin`           | `admin123`      | Administrador             |
| `gerente1`        | `gerente123`    | Gerente                   |
| `ventas1`         | `ventas123`     | Empleado de Ventas        |
| `caja1`           | `caja123`       | Empleado de Caja          |
| `mantenimiento1`  | `mantenimiento123` | Empleado de Mantenimiento |
| `cliente1`        | `cliente123`    | Cliente                   |

## Estructura del Proyecto
```text
Final_BDD/
├── src/                 # Código fuente principal
│   ├── services/        # Lógica de negocio (reportes, roles)
│   ├── views/           # Interfaces y ventanas
│   ├── auth.py          # Manejo de autenticación
│   ├── config.py        # Configuración global
│   ├── db_manager.py    # Gestor de base de datos principal
│   └── sqlite_manager.py# Gestor de la base local SQLite
├── data/                # Esquemas y datos de ejemplo
├── ui/                  # Archivos .ui para PyQt5
├── tests/               # Pruebas unitarias
├── main.py              # Punto de entrada de la aplicación
└── requirements.txt     # Dependencias
```

## Modo Offline y Sincronización
- **Modo Online (MySQL/MariaDB)**: todas las operaciones se realizan en la base remota.
- **Modo Offline (SQLite)**: si no hay conexión, la aplicación utiliza la base local para seguir operando.
- Al restablecerse la conexión los datos pendientes se sincronizan automáticamente.
- Cuenta con un mecanismo de reconexión que intenta enlazar nuevamente con la base remota y reanuda la sincronización.
- Las tablas `Alquiler`, `Reserva_alquiler` y `Abono_reserva` se particionan anualmente en MySQL; en SQLite solo se conserva la última semana de registros.
- Las reservas registran el `id_empleado` que las crea. Si un cliente genera una
  reserva por su cuenta, este campo queda en `NULL`.

## Roles y Permisos
- **Cliente**: puede crear y consultar sus reservas, editar su perfil y realizar abonos.
- Todos los empleados están vinculados a una sede específica y solo pueden gestionar datos de esa sede.
- **Empleado de Ventas**: administra clientes y reservas de su sede.
- **Empleado de Caja**: procesa y aprueba pagos únicamente para su sede.
- **Empleado de Mantenimiento**: gestiona mantenimientos de vehículos de su sede.
- **Gerente**: administra empleados y accede a reportes de ventas de su sede.
- **Administrador**: controla a los gerentes, accede a todas las consultas y puede ejecutar SQL libre.

## Sistema de Autenticación
- Contraseñas cifradas con SHA‑256.
- Bloqueo temporal del usuario tras tres intentos fallidos de inicio de sesión.
- Validación de correos únicos en tiempo real.
- Triggers automáticos que crean un usuario al registrar un cliente o un empleado.

## Sistema de Abonos
- Pestaña dedicada para realizar pagos parciales de las reservas.
- El primer abono debe cubrir al menos el 30 % del valor total.
- Se admiten abonos posteriores de cualquier valor hasta saldar la reserva.
- Soporta pago en efectivo, tarjeta o transferencia (con pasarela simulada).
- La tabla de abonos se actualiza en tiempo real y permite realizar varios pagos consecutivos sin reiniciar la vista.

## Logging
Toda la actividad relevante se almacena en el archivo `app.log`:
- Intentos de inicio de sesión y bloqueos temporales.
- Consultas y errores de la base de datos.
- Sincronización entre la base remota y local.
- Registro de pagos y cambios de contraseña.

## Ejecutar Pruebas
Las pruebas unitarias se encuentran en el directorio `tests` y utilizan `pytest`.
Para ejecutarlas desde el entorno virtual:
```bash
pytest
```
Estas pruebas validan los cálculos de los reportes de ventas usando una base SQLite temporal.

## Contribuir
1. Realiza un fork del proyecto y crea una rama para tu aportación.
2. Envía tus cambios mediante un pull request descriptivo.
3. Asegúrate de seguir la estructura y estilo del código existente.

## Licencia
El proyecto está disponible bajo la [Licencia MIT](LICENSE).

## Desarrolladores y Soporte
- **William Diaz** – Desarrollo principal.
- **Equipo de Base de Datos** – Diseño de esquemas y pruebas.

Para reportar errores o solicitar nuevas características abre un issue en el repositorio.

---
**¡Gracias por usar nuestro Sistema de Alquiler de Vehículos!** 🚗✨
