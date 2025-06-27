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

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Final_BDD
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Copia el archivo `.env.example` a `.env` y configura las variables:

```env
# Configuración de base de datos remota
DB_REMOTE_HOST=tu_servidor_mysql
DB_REMOTE_USER=tu_usuario
DB_REMOTE_PASSWORD=tu_contraseña
DB_REMOTE_NAME=nombre_base_datos

# Configuración de base de datos local
LOCAL_DB_PATH=data/local.sqlite
```

### 6. Configurar base de datos
```bash
# Ejecutar script de base de datos remota
mysql -u tu_usuario -p tu_base_datos < data/sql_bases-2.sql

# Insertar datos de prueba (opcional)
mysql -u tu_usuario -p tu_base_datos < data/inserts_prueba.sql
```

## 🚀 Ejecutar la Aplicación

```bash
python main.py
```

## 👥 Roles y Permisos

### Cliente
- Ver y crear reservas propias
- Ver vehículos disponibles
- Editar perfil personal
- Realizar abonos
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
│   ├── models/          # Modelos de datos
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
├── tests/               # Pruebas automáticas
├── main.py              # Punto de entrada
└── requirements.txt     # Dependencias
```

## 🧪 Pruebas

### Ejecutar todas las pruebas
```bash
pytest tests/
```

### Prueba específica de reservas offline
```bash
pytest tests/test_reserva_offline.py
```

### Prueba de conexión a base de datos
```bash
python test_db_connection.py
```

## 📝 Logging

La aplicación registra todos los eventos importantes en `app.log`:

- Intentos de login (exitosos y fallidos)
- Operaciones de base de datos
- Errores de conexión
- Sincronización de datos
- Cambios de contraseña

### Configuración de logging
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

## 🔧 Configuración Avanzada

### Variables de Entorno Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_REMOTE_HOST` | Servidor de base de datos | localhost |
| `DB_REMOTE_USER` | Usuario de base de datos | root |
| `DB_REMOTE_PASSWORD` | Contraseña de base de datos | - |
| `DB_REMOTE_NAME` | Nombre de la base de datos | alquiler_vehiculos |
| `LOCAL_DB_PATH` | Ruta de SQLite local | data/local.sqlite |

### Configuración de Timeout
- Timeout de conexión: 10 segundos
- Reintentos automáticos de conexión
- Cambio automático a modo offline

## 🐛 Solución de Problemas

### Error: "Unread result found"
**Problema**: Error al obtener el ID del último registro insertado en MySQL.

**Solución**: Ya corregido en la versión actual. El sistema usa `return_lastrowid=True` para evitar este error.

### Error: PyQt5 se cuelga al conectar a MySQL
**Problema**: PyQt5 interfiere con la conexión MySQL en Windows.

**Solución**: La aplicación prueba la conexión antes de importar PyQt5.

### Error: No se puede conectar a la base de datos
**Solución**:
1. Verificar que el servidor MySQL esté ejecutándose
2. Comprobar las credenciales en `.env`
3. Verificar la conectividad de red
4. La aplicación funcionará en modo offline si no hay conexión

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