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

CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    contrasena TEXT,
    id_rol INTEGER,
    id_cliente INTEGER,
    id_empleado INTEGER
);

CREATE TRIGGER IF NOT EXISTS trg_cliente_usuario
AFTER INSERT ON Cliente
BEGIN
    INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente)
    VALUES (NEW.correo, NEW.documento, 1, NEW.id_cliente);
END;
