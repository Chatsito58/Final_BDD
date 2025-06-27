CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT,
    nombre TEXT,
    telefono TEXT,
    correo TEXT,
    pendiente INTEGER DEFAULT 1
);

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

CREATE TABLE IF NOT EXISTS Alquiler (
    id_alquiler INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora_salida TEXT,
    valor REAL,
    fecha_hora_entrada TEXT,
    id_vehiculo TEXT,
    id_cliente INTEGER,
    id_sucursal INTEGER,
    id_medio_pago INTEGER,
    id_estado INTEGER,
    id_seguro INTEGER,
    id_descuento INTEGER
);

CREATE TABLE IF NOT EXISTS Reserva_alquiler (
    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT,
    abono REAL,
    saldo_pendiente REAL,
    id_estado_reserva INTEGER,
    id_alquiler INTEGER,
    FOREIGN KEY (id_alquiler) REFERENCES Alquiler(id_alquiler)
);

CREATE TABLE IF NOT EXISTS Abono_reserva (
    id_abono INTEGER PRIMARY KEY AUTOINCREMENT,
    valor REAL,
    fecha_hora TEXT,
    id_reserva INTEGER,
    id_medio_pago INTEGER,
    FOREIGN KEY (id_reserva) REFERENCES Reserva_alquiler(id_reserva)
);

CREATE TABLE IF NOT EXISTS Estado_reserva (
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Descuento_alquiler (
    id_descuento INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT,
    valor REAL
);

CREATE TABLE IF NOT EXISTS Seguro_alquiler (
    id_seguro INTEGER PRIMARY KEY AUTOINCREMENT,
    estado TEXT,
    descripcion TEXT,
    vencimiento TEXT,
    costo REAL
);

CREATE TABLE IF NOT EXISTS Rol (
    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT
);

CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    contrasena TEXT,
    id_rol INTEGER,
    id_cliente INTEGER,
    id_empleado INTEGER
);

CREATE TABLE IF NOT EXISTS Empleado (
    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT,
    nombre TEXT,
    telefono TEXT,
    correo TEXT,
    cargo TEXT
);

-- Insertar roles básicos
INSERT OR IGNORE INTO Rol (id_rol, nombre) VALUES 
(1, 'cliente'),
(2, 'empleado'),
(3, 'gerente'),
(4, 'admin');

CREATE TRIGGER IF NOT EXISTS trg_cliente_usuario
AFTER INSERT ON Cliente
BEGIN
    INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente)
    VALUES (NEW.correo, NEW.documento, 1, NEW.id_cliente);
END;

CREATE TRIGGER IF NOT EXISTS trg_empleado_usuario
AFTER INSERT ON Empleado
BEGIN
    INSERT INTO Usuario (usuario, contrasena, id_rol, id_empleado)
    VALUES (NEW.correo, NEW.documento, 2, NEW.id_empleado);
END;

-- Tablas críticas para sincronización offline
CREATE TABLE IF NOT EXISTS Tipo_documento (
    id_tipo_documento INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Codigo_postal (
    id_codigo_postal TEXT PRIMARY KEY,
    pais TEXT,
    departamento TEXT,
    ciudad TEXT
);

CREATE TABLE IF NOT EXISTS Tipo_cliente (
    id_tipo INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Estado_vehiculo (
    id_estado INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Marca_vehiculo (
    id_marca INTEGER PRIMARY KEY,
    nombre_marca TEXT
);

CREATE TABLE IF NOT EXISTS Color_vehiculo (
    id_color INTEGER PRIMARY KEY,
    nombre_color TEXT
);

CREATE TABLE IF NOT EXISTS Tipo_vehiculo (
    id_tipo INTEGER PRIMARY KEY,
    descripcion TEXT,
    capacidad INTEGER,
    combustible TEXT,
    tarifa_dia REAL
);

CREATE TABLE IF NOT EXISTS Blindaje_vehiculo (
    id_blindaje INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Transmision_vehiculo (
    id_transmision INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Cilindraje_vehiculo (
    id_cilindraje INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Sucursal (
    id_sucursal INTEGER PRIMARY KEY,
    nombre TEXT,
    direccion TEXT,
    telefono TEXT,
    gerente TEXT,
    id_codigo_postal TEXT
);

CREATE TABLE IF NOT EXISTS Seguro_vehiculo (
    id_seguro INTEGER PRIMARY KEY,
    estado TEXT,
    descripcion TEXT,
    vencimiento TEXT,
    costo REAL
);

CREATE TABLE IF NOT EXISTS Tipo_empleado (
    id_tipo_empleado INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Medio_pago (
    id_medio_pago INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Estado_alquiler (
    id_estado INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Licencia_conduccion (
    id_licencia INTEGER PRIMARY KEY,
    estado TEXT,
    fecha_emision TEXT,
    fecha_vencimiento TEXT,
    id_categoria INTEGER
);

CREATE TABLE IF NOT EXISTS Categoria_licencia (
    id_categoria INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Taller_mantenimiento (
    id_taller INTEGER PRIMARY KEY,
    nombre TEXT,
    direccion TEXT,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS Tipo_mantenimiento (
    id_tipo INTEGER PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS Proveedor_vehiculo (
    id_proveedor INTEGER PRIMARY KEY,
    nombre TEXT,
    direccion TEXT,
    telefono TEXT,
    correo TEXT
);
