-- Crear roles
INSERT INTO Rol (nombre) VALUES ('cliente'), ('empleado'), ('gerente'), ('admin');

-- Tipos y catálogos
INSERT INTO Tipo_entidad (descripcion) VALUES ('Persona natural'), ('Empresa');
INSERT INTO Medio_pago (descripcion) VALUES ('Efectivo'), ('Tarjeta'), ('Transferencia');
INSERT INTO Tipo_documento (descripcion) VALUES ('CC'), ('CE'), ('NIT');
INSERT INTO Codigo_postal (id_codigo_postal, pais, departamento, ciudad) VALUES ('110111', 'Colombia', 'Cundinamarca', 'Bogotá'), ('760001', 'Colombia', 'Valle del Cauca', 'Cali');
INSERT INTO Categoria_licencia (descripcion) VALUES ('B1'), ('C1');
INSERT INTO Tipo_mantenimiento (descripcion) VALUES ('Preventivo'), ('Correctivo');
INSERT INTO Taller_mantenimiento (nombre, direccion, telefono) VALUES ('Taller Central', 'Cra 10 #20-30, Bogotá', '3101234567');
INSERT INTO Estado_vehiculo (descripcion) VALUES ('Disponible'), ('En mantenimiento');
INSERT INTO Marca_vehiculo (nombre_marca) VALUES ('Renault'), ('Chevrolet');
INSERT INTO Color_vehiculo (nombre_color) VALUES ('Blanco'), ('Rojo');
INSERT INTO Tipo_vehiculo (descripcion, capacidad, combustible, tarifa_dia) VALUES ('Sedán', 5, 'Gasolina', 120000), ('SUV', 7, 'Diesel', 180000);
INSERT INTO Blindaje_vehiculo (descripcion) VALUES ('Ninguno'), ('Nivel 2');
INSERT INTO Transmision_vehiculo (descripcion) VALUES ('Manual'), ('Automática');
INSERT INTO Cilindraje_vehiculo (descripcion) VALUES ('1600cc'), ('2000cc');
INSERT INTO Estado_alquiler (descripcion) VALUES ('Activa'), ('Finalizada');

-- Estados de reserva
INSERT INTO Estado_reserva (descripcion) VALUES ('Pendiente'), ('Confirmada'), ('Cancelada');

-- Sucursal y proveedor
INSERT INTO Sucursal (nombre, direccion, telefono, gerente, id_codigo_postal)
VALUES
    ('Sucursal Norte', 'Av 68 #100-20, Bogotá', '3209876543', 'Ana Gerente', '110111'),
    ('Sucursal Sur', 'Cra 15 #50-40, Cali', '3211234567', 'Juan Gerente', '760001');
INSERT INTO Proveedor_vehiculo (nombre, direccion, telefono, correo) VALUES ('Autocolombia', 'Calle 80 #30-15, Bogotá', '3152223344', 'ventas@autocolombia.com');

-- Licencia de conducción
INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES ('Vigente', '2022-01-10', '2027-01-10', 1);

-- Clientes y empleados
INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, id_licencia, id_tipo_documento, id_codigo_postal) VALUES ('987654321', 'Carlos Ramírez', '3111111111', 'Calle 12 #34-56, Bogotá', 'carlos.ramirez@email.com', 1, 1, '110111');

-- Tipos de empleado (jerarquía)
INSERT INTO Tipo_empleado (descripcion) VALUES ('admin'), ('gerente'), ('ventas'), ('caja'), ('mantenimiento');

-- Empleados de cada tipo
INSERT INTO Empleado (documento, nombre, salario, cargo, telefono, direccion, correo, id_sucursal, id_tipo_documento, id_tipo_empleado) VALUES
('100000001', 'Admin Principal', 5000000, 'Administrador', '3000000001', 'Calle 1 #1-01', 'admin@email.com', 1, 1, 1),
('100000002', 'Gerente General', 4000000, 'Gerente', '3000000002', 'Calle 2 #2-02', 'gerente@email.com', 1, 1, 2),
('100000003', 'Vendedor Uno', 2500000, 'Ventas', '3000000003', 'Calle 3 #3-03', 'ventas@email.com', 1, 1, 3),
('100000004', 'Cajero Uno', 2200000, 'Caja', '3000000004', 'Calle 4 #4-04', 'caja@email.com', 1, 1, 4),
('100000005', 'Mantenimiento Uno', 2300000, 'Mantenimiento', '3000000005', 'Calle 5 #5-05', 'mantenimiento@email.com', 2, 1, 5);

-- Seguros de vehículos
INSERT INTO Seguro_vehiculo (estado, descripcion, vencimiento, costo) VALUES
('Vigente', 'SOAT', '2025-12-31', 150000),
('Vigente', 'Todo riesgo', '2025-12-31', 300000);

-- Vehículos de prueba
INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_blindaje, id_transmision, id_cilindraje, id_seguro_vehiculo, id_estado_vehiculo, id_proveedor, id_sucursal)
VALUES
('ABC123', 'CHS123456', 'Logan 2020', 25000, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1),
('XYZ789', 'CHS654321', 'Captiva 2022', 12000, 2, 2, 2, 2, 1, 2, 2, 1, 1, 1);

-- Seguros de alquiler
INSERT INTO Seguro_alquiler (estado, descripcion, vencimiento, costo) VALUES
('Vigente', 'Seguro todo riesgo', '2025-12-31', 50000),
('Vigente', 'Seguro básico', '2025-12-31', 20000);

-- Descuentos de alquiler
INSERT INTO Descuento_alquiler (descripcion, valor, fecha_inicio, fecha_fin) VALUES
('Descuento 10%', 30000, '2024-01-01 00:00:00', '2024-12-31 23:59:59'),
('Sin descuento', 0, '2024-01-01 00:00:00', '2030-12-31 23:59:59');

-- Alquileres de Carlos Ramírez
INSERT INTO Alquiler (fecha_hora_salida, valor, fecha_hora_entrada, id_vehiculo, id_cliente, id_empleado, id_sucursal, id_medio_pago, id_estado, id_seguro, id_descuento)
VALUES
    ('2024-06-01 10:00:00', 210000, '2024-06-03 10:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 1),
    ('2024-06-10 09:00:00', 200000, '2024-06-11 09:00:00', 'XYZ789', 1, 4, 1, 2, 1, 2, 2),
    ('2024-07-05 08:00:00', 150000, '2024-07-06 08:00:00', 'ABC123', 1, 4, 1, 1, 1, 1, 2),
    ('2024-07-12 15:00:00', 170000, '2024-07-13 15:00:00', 'XYZ789', 1, 3, 2, 2, 1, 2, 1),
    ('2024-07-20 09:00:00', 190000, '2024-07-22 09:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 2),
    ('2024-08-02 10:00:00', 250000, '2024-08-04 10:00:00', 'XYZ789', 1, 4, 2, 2, 1, 2, 1),
    ('2024-08-15 08:00:00', 230000, '2024-08-16 08:00:00', 'ABC123', 1, 3, 1, 1, 1, 1, 1);

-- Reservas de Carlos Ramírez
INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler)
VALUES
    ('2024-05-30 09:00:00', 100000, 110000, 1, 1),
    ('2024-06-08 08:00:00', 50000, 150000, 1, 2),
    ('2024-07-04 07:00:00', 60000, 90000, 1, 3),
    ('2024-07-11 14:00:00', 70000, 100000, 1, 4),
    ('2024-07-18 10:00:00', 90000, 100000, 1, 5),
    ('2024-08-01 12:00:00', 75000, 175000, 1, 6),
    ('2024-08-14 13:00:00', 70000, 160000, 1, 7);

-- Abonos a reservas
INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES
    (100000, '2024-05-30 10:00:00', 1, 1),
    (50000, '2024-06-08 09:00:00', 2, 2),
    (60000, '2024-07-04 08:00:00', 3, 1),
    (70000, '2024-07-11 15:00:00', 4, 2),
    (90000, '2024-07-18 11:00:00', 5, 1),
    (75000, '2024-08-01 13:00:00', 6, 2),
    (70000, '2024-08-14 14:00:00', 7, 1);
