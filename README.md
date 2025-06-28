# Sistema de Alquiler de Vehículos

Este repositorio contiene una aplicación completa de alquiler de vehículos desarrollada en Python con interfaz gráfica moderna y sistema de bases de datos redundante.

## 🚗 Características Principales

- **Interfaz gráfica moderna** con PyQt5 y CustomTkinter
- **Sistema de autenticación** con roles y permisos
- **Base de datos redundante** (MariaDB/MySQL + SQLite)
- **Modo offline** con sincronización automática
- **Gestión completa** de clientes, empleados, vehículos y reservas
- **Sistema de pagos** integrado
- **Interfaz responsiva** y fácil de usar
- **Flujo de registro mejorado** con retorno automático al login

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.8+
- **Bases de datos**: MariaDB/MySQL (principal), SQLite (local)
- **Interfaces**: PyQt5, CustomTkinter
- **Autenticación**: SHA-256
- **Logging**: Sistema centralizado de logs

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- MariaDB/MySQL (opcional, para modo online)
- Conexión a internet (para sincronización inicial)

## 🚀 Instalación y Configuración Completa

### Paso 1: Instalar Python

#### Windows:
1. Ve a [python.org](https://www.python.org/downloads/)
2. Descarga la versión más reciente de Python (3.8 o superior)
3. Ejecuta el instalador
4. **IMPORTANTE**: Marca la casilla "Add Python to PATH"
5. Haz clic en "Install Now"

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Linux (CentOS/RHEL/Fedora):
```bash
sudo dnf install python3 python3-pip python3-venv
# O para versiones más antiguas:
sudo yum install python3 python3-pip python3-venv
```

#### macOS:
```bash
# Con Homebrew (recomendado)
brew install python3

# O descarga desde python.org
```

### Paso 2: Verificar la instalación

Abre una terminal (Command Prompt en Windows) y ejecuta:

```bash
python --version
# Debe mostrar Python 3.8.x o superior

pip --version
# Debe mostrar pip instalado
```

### Paso 3: Descargar el proyecto

#### Opción A: Clonar con Git
```bash
git clone <url-del-repositorio>
cd Final_BDD
```

#### Opción B: Descargar ZIP
1. Ve al repositorio en GitHub
2. Haz clic en "Code" → "Download ZIP"
3. Extrae el archivo ZIP
4. Abre una terminal en la carpeta extraída

### Paso 4: Crear entorno virtual

#### Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Nota**: Deberías ver `(venv)` al inicio de la línea de comandos, indicando que el entorno virtual está activado.

### Paso 5: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 6: Configurar variables de entorno

1. Copia el archivo de ejemplo:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/macOS
   cp .env.example .env
   ```

2. Edita el archivo `.env` con tus configuraciones:

```env
# Configuración de base de datos remota (opcional)
DB_REMOTE_HOST=localhost
DB_REMOTE_PORT=3306
DB_REMOTE_USER=root
DB_REMOTE_PASSWORD=tu_contraseña
DB_REMOTE_NAME=alquiler_vehiculos

# Configuración de base de datos local
LOCAL_DB_PATH=data/local.sqlite
```

**Nota**: Si no tienes MySQL/MariaDB, puedes dejar las configuraciones por defecto. La aplicación funcionará en modo offline con SQLite.

### Paso 7: Configurar base de datos (Opcional)

#### Si tienes MySQL/MariaDB instalado:

1. **Instalar MySQL/MariaDB**:

   **Windows**:
   - Descarga MySQL Installer desde [mysql.com](https://dev.mysql.com/downloads/installer/)
   - Ejecuta el instalador y sigue las instrucciones
   - Anota la contraseña del usuario root

   **Linux (Ubuntu/Debian)**:
   ```bash
   sudo apt install mysql-server
   sudo mysql_secure_installation
   ```

   **Linux (CentOS/RHEL/Fedora)**:
   ```bash
   sudo dnf install mysql-server
   sudo systemctl start mysqld
   sudo mysql_secure_installation
   ```

   **macOS**:
   ```bash
   brew install mysql
   brew services start mysql
   ```

2. **Crear la base de datos**:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE alquiler_vehiculos;
   USE alquiler_vehiculos;
   SOURCE data/sql_bases-2.sql;
   SOURCE data/inserts_prueba.sql;
   EXIT;
   ```

#### Si NO tienes MySQL/MariaDB:
La aplicación funcionará automáticamente en modo offline con SQLite. No necesitas hacer nada más.

### Paso 8: Ejecutar la aplicación

```bash
python main.py
```

¡Listo! La aplicación debería abrirse con la ventana de login.

## 👥 Usuarios de Prueba

La aplicación incluye usuarios de prueba para cada rol:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador |
| `gerente1` | `gerente123` | Gerente |
| `ventas1` | `ventas123` | Empleado de Ventas |
| `caja1` | `caja123` | Empleado de Caja |
| `mantenimiento1` | `mantenimiento123` | Empleado de Mantenimiento |
| `cliente1` | `cliente123` | Cliente |

## 💳 Realizar Abonos a Reservas

### Instrucciones para Clientes

1. **Acceder a la pestaña "Realizar abonos"**:
   - Inicia sesión como cliente
   - Ve a la pestaña "Realizar abonos"

2. **Seleccionar reserva**:
   - La lista muestra todas las reservas con saldo pendiente
   - Selecciona la reserva a la que quieres hacer abono

3. **Ingresar monto**:
   - **Primer abono**: Debe ser al menos el 30% del valor total
   - **Abonos posteriores**: Pueden ser de cualquier valor
   - El sistema valida que no exceda el saldo pendiente

4. **Seleccionar método de pago**:
   - **Efectivo**: Registra el abono y muestra mensaje para validar en oficina
   - **Tarjeta/Transferencia**: Abre pasarela de pagos simulada

5. **Confirmar abono**:
   - El sistema registra el abono automáticamente
   - Actualiza el saldo pendiente de la reserva
   - Muestra confirmación del pago realizado

## 🔧 Configuración del Puerto

El puerto de la base de datos se configura en el archivo `.env`:

```env
DB_REMOTE_PORT=3306
```

**Puertos comunes**:
- **3306**: Puerto estándar de MySQL/MariaDB
- **3307**: Puerto alternativo común
- **33060**: Puerto X Protocol de MySQL

## 🚀 Comandos Rápidos por Sistema Operativo

### Windows (Command Prompt)
```cmd
# Instalar dependencias
pip install -r requirements.txt

# Activar entorno virtual
venv\Scripts\activate

# Ejecutar aplicación
python main.py
```

### Windows (PowerShell)
```powershell
# Instalar dependencias
pip install -r requirements.txt

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar aplicación
python main.py
```

### Linux/macOS
```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
python main.py
```

## 🔄 Sistema de Base de Datos Redundante

### Modo Online (MariaDB/MySQL)
- Base de datos principal
- Todas las operaciones se realizan aquí
- Sincronización automática con SQLite

### Modo Offline (SQLite)
- Base de datos local de respaldo
- Se activa automáticamente cuando no hay conexión
- Permite continuar trabajando sin internet
- Sincronización automática cuando vuelve la conexión

### Sincronización Automática
- Los datos se sincronizan automáticamente entre ambas bases
- Las reservas creadas offline se suben cuando hay conexión
- No se pierden datos por problemas de conectividad

## 👥 Roles y Permisos

### Cliente
- Ver y crear reservas propias
- Ver vehículos disponibles
- Editar perfil personal
- Realizar abonos a reservas pendientes
- Cambiar contraseña

### Empleado de Ventas
- Gestionar clientes
- Crear y editar reservas
- Consultar vehículos
- Cambiar contraseña

### Empleado de Caja
- Procesar pagos
- Consultar reservas
- Ver clientes
- Cambiar contraseña

### Empleado de Mantenimiento
- Ver vehículos asignados
- Reportar mantenimiento
- Ver historial de vehículos
- Cambiar contraseña

### Gerente
- Gestionar empleados (excepto gerentes y admin)
- Ver todos los clientes
- Generar reportes de sucursal
- Cambiar contraseña

### Administrador
- Gestionar gerentes
- Ver todos los empleados y clientes
- Ejecutar consultas SQL libres
- Cambiar contraseña

## 🔐 Sistema de Autenticación

### Características de Seguridad
- Contraseñas cifradas con SHA-256
- Bloqueo temporal tras 3 intentos fallidos
- Validación de correo único
- Triggers automáticos para crear usuarios

### Triggers Automáticos
- Al registrar un **Cliente**: se crea automáticamente un usuario con rol 'cliente'
- Al registrar un **Empleado**: se crea automáticamente un usuario con rol 'empleado'

## 📊 Estructura del Proyecto

```
Final_BDD/
├── src/
│   ├── services/        # Lógica de negocio
│   ├── views/           # Interfaces de usuario
│   ├── auth.py          # Autenticación
│   ├── config.py        # Configuración
│   ├── db_manager.py    # Gestor de base de datos
│   └── sqlite_manager.py # Gestor SQLite
├── data/
│   ├── sql_bases-2.sql  # Esquema MariaDB
│   ├── sqlite_schema.sql # Esquema SQLite
│   └── inserts_prueba.sql # Datos de prueba
├── ui/                  # Archivos de interfaz
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
├── .env.example         # Configuración de ejemplo
└── README.md           # Este archivo
```

## 📝 Logging

La aplicación registra todos los eventos importantes en `app.log`:

- Intentos de login (exitosos y fallidos)
- Operaciones de base de datos
- Errores de conexión
- Sincronización de datos
- Cambios de contraseña

## 🔧 Variables de Entorno Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_REMOTE_HOST` | Servidor de base de datos | localhost |
| `DB_REMOTE_PORT` | Puerto de base de datos | 3306 |
| `DB_REMOTE_USER` | Usuario de base de datos | root |
| `DB_REMOTE_PASSWORD` | Contraseña de base de datos | - |
| `DB_REMOTE_NAME` | Nombre de la base de datos | alquiler_vehiculos |
| `LOCAL_DB_PATH` | Ruta de SQLite local | data/local.sqlite |

## 🐛 Solución de Problemas Comunes

### Error: "python no se reconoce como comando"
**Solución**: 
1. Reinstala Python marcando "Add Python to PATH"
2. O usa `python3` en lugar de `python`

### Error: "pip no se reconoce como comando"
**Solución**:
```bash
# Windows
python -m pip install -r requirements.txt

# Linux/macOS
python3 -m pip install -r requirements.txt
```

### Error: "No se puede conectar a la base de datos"
**Solución**:
1. Verificar que el servidor MySQL esté ejecutándose
2. Comprobar las credenciales en `.env`
3. Verificar la conectividad de red
4. La aplicación funcionará en modo offline si no hay conexión

### Error: "ModuleNotFoundError"
**Solución**:
1. Asegúrate de que el entorno virtual esté activado
2. Reinstala las dependencias: `pip install -r requirements.txt`

### Error: "Permission denied" (Linux/macOS)
**Solución**:
```bash
chmod +x main.py
```

## 📈 Características Recientes (2024)

### Interfaz Moderna
- Diseño oscuro y moderno
- Indicadores visuales de estado de conexión
- Navegación mejorada entre ventanas

### Funcionalidades Avanzadas
- Selección visual de fecha y hora en reservas
- Sistema de pagos integrado
- Gestión completa de abonos
- Reportes automáticos

### Robustez del Sistema
- Sincronización automática de datos críticos
- Manejo robusto de desconexiones
- Logging detallado de todas las operaciones
- Validación de integridad de datos

### Flujo de Registro Mejorado
- Registro de clientes con retorno automático al login
- Prellenado del correo electrónico después del registro
- Triggers automáticos para crear usuarios con contraseñas seguras
- Validación de correos únicos en tiempo real

### Sistema de Abonos para Clientes
- Pestaña dedicada para realizar abonos a reservas pendientes
- Validación del 30% mínimo para el primer abono
- Abonos posteriores de cualquier valor
- Selección de método de pago (Efectivo, Tarjeta, Transferencia)
- Pasarela de pagos simulada para tarjeta y transferencia
- Mensajes informativos según el método de pago seleccionado
- Actualización automática del saldo pendiente

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Desarrolladores

- **William Diaz** - Desarrollo principal
- **Equipo de Base de Datos** - Diseño de esquemas

## 📞 Soporte

Para reportar bugs o solicitar nuevas características, por favor abre un issue en el repositorio.

---

**¡Gracias por usar nuestro Sistema de Alquiler de Vehículos!** 🚗✨ 

2. **Contraseña inicial**: El número de documento del cliente
3. **Cambio de contraseña**: Disponible después del primer login

### Realizar Abonos a Reservas

1. **Acceder a la pestaña "Realizar abonos"**:
   - Inicia sesión como cliente
   - Ve a la pestaña "Realizar abonos"

2. **Seleccionar reserva**:
   - La lista muestra todas las reservas con saldo pendiente
   - Selecciona la reserva a la que quieres hacer abono

3. **Ingresar monto**:
   - **Primer abono**: Debe ser al menos el 30% del valor total
   - **Abonos posteriores**: Pueden ser de cualquier valor
   - El sistema valida que no exceda el saldo pendiente

4. **Seleccionar método de pago**:
   - **Efectivo**: Registra el abono y muestra mensaje para validar en oficina
   - **Tarjeta/Transferencia**: Abre pasarela de pagos simulada

5. **Confirmar abono**:
   - El sistema registra el abono automáticamente
   - Actualiza el saldo pendiente de la reserva
   - Muestra confirmación del pago realizado 