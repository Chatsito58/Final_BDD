CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT,
    nombre TEXT,
    telefono TEXT,
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
