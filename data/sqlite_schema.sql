-- SQLite schema updated to match the new database structure from sql_bases.sql

-- Tablas principales del sistema
CREATE TABLE IF NOT EXISTS Tipo_entidad (
  id_tipo_entidad INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Medio_pago (
  id_medio_pago INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tipo_documento (
  id_tipo_documento INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Codigo_postal (
  id_codigo_postal TEXT NOT NULL PRIMARY KEY,
  pais TEXT NOT NULL,
  departamento TEXT NOT NULL,
  ciudad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Categoria_licencia (
  id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tipo_mantenimiento (
  id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Taller_mantenimiento (
  id_taller INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  direccion TEXT,
  telefono TEXT
);

CREATE TABLE IF NOT EXISTS Estado_vehiculo (
  id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Marca_vehiculo (
  id_marca INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_marca TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Color_vehiculo (
  id_color INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_color TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tipo_vehiculo (
  id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL,
  capacidad INTEGER,
  combustible TEXT,
  tarifa_dia REAL
);

CREATE TABLE IF NOT EXISTS Blindaje_vehiculo (
  id_blindaje INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Transmision_vehiculo (
  id_transmision INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Cilindraje_vehiculo (
  id_cilindraje INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Estado_alquiler (
  id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Sucursal (
  id_sucursal INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  direccion TEXT,
  telefono TEXT,
  gerente TEXT,
  id_codigo_postal TEXT,
  FOREIGN KEY (id_codigo_postal) REFERENCES Codigo_postal(id_codigo_postal)
);

CREATE TABLE IF NOT EXISTS Tipo_empleado (
  id_tipo_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Empleado (
  id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
  documento TEXT NOT NULL,
  nombre TEXT NOT NULL,
  salario REAL,
  cargo TEXT,
  telefono TEXT,
  direccion TEXT,
  correo TEXT,
  id_sucursal INTEGER NOT NULL,
  id_tipo_documento INTEGER,
  id_tipo_empleado INTEGER,
  FOREIGN KEY (id_tipo_documento) REFERENCES Tipo_documento(id_tipo_documento),
  FOREIGN KEY (id_tipo_empleado) REFERENCES Tipo_empleado(id_tipo_empleado),
  FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal)
);

CREATE TABLE IF NOT EXISTS Licencia_conduccion (
  id_licencia INTEGER PRIMARY KEY AUTOINCREMENT,
  estado TEXT,
  fecha_emision TEXT,
  fecha_vencimiento TEXT,
  id_categoria INTEGER,
  FOREIGN KEY (id_categoria) REFERENCES Categoria_licencia(id_categoria)
);

CREATE TABLE IF NOT EXISTS Cliente (
  id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
  documento TEXT NOT NULL,
  nombre TEXT NOT NULL,
  telefono TEXT,
  direccion TEXT,
  correo TEXT UNIQUE,
  infracciones INTEGER DEFAULT 0,
  id_licencia INTEGER,
  id_tipo_documento INTEGER,
  id_codigo_postal TEXT,
  id_cuenta INTEGER,
  pendiente INTEGER DEFAULT 1,
  FOREIGN KEY (id_licencia) REFERENCES Licencia_conduccion(id_licencia),
  FOREIGN KEY (id_tipo_documento) REFERENCES Tipo_documento(id_tipo_documento),
  FOREIGN KEY (id_codigo_postal) REFERENCES Codigo_postal(id_codigo_postal)
);

CREATE TABLE IF NOT EXISTS Seguro_vehiculo (
  id_seguro INTEGER PRIMARY KEY AUTOINCREMENT,
  estado TEXT,
  descripcion TEXT,
  vencimiento TEXT,
  costo REAL
);

CREATE TABLE IF NOT EXISTS Proveedor_vehiculo (
  id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT,
  direccion TEXT,
  telefono TEXT,
  correo TEXT,
  id_cuenta INTEGER
);

CREATE TABLE IF NOT EXISTS Vehiculo (
  placa TEXT PRIMARY KEY,
  n_chasis TEXT,
  modelo TEXT,
  kilometraje INTEGER,
  id_marca INTEGER,
  id_color INTEGER,
  id_tipo_vehiculo INTEGER,
  id_blindaje INTEGER,
  id_transmision INTEGER,
  id_cilindraje INTEGER,
  id_seguro_vehiculo INTEGER,
  id_estado_vehiculo INTEGER DEFAULT 1,
  id_proveedor INTEGER,
  id_sucursal INTEGER,
  FOREIGN KEY (id_marca) REFERENCES Marca_vehiculo(id_marca),
  FOREIGN KEY (id_color) REFERENCES Color_vehiculo(id_color),
  FOREIGN KEY (id_tipo_vehiculo) REFERENCES Tipo_vehiculo(id_tipo),
  FOREIGN KEY (id_blindaje) REFERENCES Blindaje_vehiculo(id_blindaje),
  FOREIGN KEY (id_transmision) REFERENCES Transmision_vehiculo(id_transmision),
  FOREIGN KEY (id_cilindraje) REFERENCES Cilindraje_vehiculo(id_cilindraje),
  FOREIGN KEY (id_seguro_vehiculo) REFERENCES Seguro_vehiculo(id_seguro),
  FOREIGN KEY (id_estado_vehiculo) REFERENCES Estado_vehiculo(id_estado),
  FOREIGN KEY (id_proveedor) REFERENCES Proveedor_vehiculo(id_proveedor),
  FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal)
);

CREATE TABLE IF NOT EXISTS Mantenimiento_vehiculo (
  id_mantenimiento INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT,
  fecha_hora TEXT,
  valor REAL,
  id_tipo INTEGER,
  id_taller INTEGER,
  id_vehiculo TEXT,
  FOREIGN KEY (id_tipo) REFERENCES Tipo_mantenimiento(id_tipo),
  FOREIGN KEY (id_taller) REFERENCES Taller_mantenimiento(id_taller),
  FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(placa)
);

CREATE TABLE IF NOT EXISTS Mantenimiento (
  id_mantenimiento INTEGER PRIMARY KEY AUTOINCREMENT,
  placa TEXT,
  descripcion TEXT,
  fecha TEXT DEFAULT (datetime('now')),
  fecha_fin TEXT,
  FOREIGN KEY (placa) REFERENCES Vehiculo(placa)
);

CREATE TABLE IF NOT EXISTS Descuento_alquiler (
  id_descuento INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT,
  valor REAL,
  fecha_inicio TEXT,
  fecha_fin TEXT
);

CREATE TABLE IF NOT EXISTS Estado_reserva (
  id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
  descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Seguro_alquiler (
  id_seguro INTEGER PRIMARY KEY AUTOINCREMENT,
  estado TEXT,
  descripcion TEXT,
  vencimiento TEXT,
  costo REAL
);

CREATE TABLE IF NOT EXISTS Alquiler (
  id_alquiler INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_hora_salida TEXT,
  valor REAL,
  fecha_hora_entrada TEXT,
  id_vehiculo TEXT,
  id_cliente INTEGER,
  id_empleado INTEGER,
  id_sucursal INTEGER,
  id_medio_pago INTEGER,
  id_estado INTEGER,
  id_seguro INTEGER,
  id_descuento INTEGER,
  FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(placa),
  FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
  FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado),
  FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal),
  FOREIGN KEY (id_medio_pago) REFERENCES Medio_pago(id_medio_pago),
  FOREIGN KEY (id_estado) REFERENCES Estado_alquiler(id_estado),
  FOREIGN KEY (id_seguro) REFERENCES Seguro_alquiler(id_seguro),
  FOREIGN KEY (id_descuento) REFERENCES Descuento_alquiler(id_descuento)
);

CREATE TABLE IF NOT EXISTS Reserva_alquiler (
  id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_hora TEXT,
  abono REAL,
  saldo_pendiente REAL,
  id_estado_reserva INTEGER,
  id_empleado INTEGER,
  id_alquiler INTEGER,
  FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado),
  FOREIGN KEY (id_estado_reserva) REFERENCES Estado_reserva(id_estado),
  FOREIGN KEY (id_alquiler) REFERENCES Alquiler(id_alquiler)
);

CREATE TABLE IF NOT EXISTS Det_factura (
  id_det_factura INTEGER PRIMARY KEY AUTOINCREMENT,
  id_servicio INTEGER,
  valor REAL,
  impuestos REAL
);

CREATE TABLE IF NOT EXISTS Factura (
  id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
  valor REAL,
  id_alquiler INTEGER,
  id_cliente INTEGER,
  id_vehiculo TEXT,
  id_det_factura INTEGER,
  FOREIGN KEY (id_alquiler) REFERENCES Alquiler(id_alquiler),
  FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
  FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(placa),
  FOREIGN KEY (id_det_factura) REFERENCES Det_factura(id_det_factura)
);

CREATE TABLE IF NOT EXISTS Cuenta_pagar (
  id_cuenta_pagar INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_hora TEXT,
  valor REAL,
  descripcion TEXT,
  id_medio_pago INTEGER,
  id_tipo_entidad INTEGER,
  id_entidad INTEGER,
  FOREIGN KEY (id_medio_pago) REFERENCES Medio_pago(id_medio_pago),
  FOREIGN KEY (id_tipo_entidad) REFERENCES Tipo_entidad(id_tipo_entidad)
);

CREATE TABLE IF NOT EXISTS Cuenta_cobrar (
  id_cuenta_cobrar INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_hora TEXT,
  valor REAL,
  descripcion TEXT,
  id_medio_pago INTEGER,
  id_tipo_entidad INTEGER,
  id_entidad INTEGER,
  FOREIGN KEY (id_medio_pago) REFERENCES Medio_pago(id_medio_pago),
  FOREIGN KEY (id_tipo_entidad) REFERENCES Tipo_entidad(id_tipo_entidad)
);

CREATE TABLE IF NOT EXISTS Cuenta (
  id_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
  id_cuenta_pagar INTEGER,
  id_cuenta_cobrar INTEGER,
  FOREIGN KEY (id_cuenta_pagar) REFERENCES Cuenta_pagar(id_cuenta_pagar),
  FOREIGN KEY (id_cuenta_cobrar) REFERENCES Cuenta_cobrar(id_cuenta_cobrar)
);

CREATE TABLE IF NOT EXISTS Abono_reserva (
  id_abono INTEGER PRIMARY KEY AUTOINCREMENT,
  valor REAL,
  fecha_hora TEXT,
  id_reserva INTEGER,
  id_medio_pago INTEGER,
  FOREIGN KEY (id_reserva) REFERENCES Reserva_alquiler(id_reserva),
  FOREIGN KEY (id_medio_pago) REFERENCES Medio_pago(id_medio_pago)
);

CREATE TABLE IF NOT EXISTS Rol (
  id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Usuario (
  id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario TEXT NOT NULL UNIQUE,
  contrasena TEXT NOT NULL,
  id_rol INTEGER,
  id_cliente INTEGER,
  id_empleado INTEGER,
  pendiente INTEGER DEFAULT 0,
  FOREIGN KEY (id_rol) REFERENCES Rol(id_rol),
  FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
  FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado)
);

-- Tabla legacy para compatibilidad (mantener por ahora)
CREATE TABLE IF NOT EXISTS Reserva (
    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora_salida TEXT,
    fecha_hora_entrada TEXT,
    id_vehiculo TEXT,
    id_cliente INTEGER,
    id_seguro INTEGER,
    id_estado INTEGER,
    pendiente INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Abono (
    id_abono INTEGER PRIMARY KEY AUTOINCREMENT,
    valor REAL,
    fecha_hora TEXT,
    id_reserva INTEGER,
    pendiente INTEGER DEFAULT 1
);

-- Insertar roles básicos
INSERT OR IGNORE INTO Rol (id_rol, nombre) VALUES 
(1, 'cliente'),
(2, 'empleado'),
(3, 'gerente'),
(4, 'admin');

-- Triggers para crear usuarios automáticamente (simplificados para SQLite)
-- Nota: Los triggers no pueden usar funciones hash complejas en SQLite
-- La creación de usuarios se manejará en el código Python

-- Queue for failed remote operations
CREATE TABLE IF NOT EXISTS retry_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT,
    table_name TEXT,
    payload TEXT,
    target TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
