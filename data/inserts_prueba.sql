-- Crear roles
INSERT INTO Rol (nombre) VALUES ('cliente'), ('empleado'), ('gerente'), ('admin');

-- Tipos y catálogos
INSERT INTO Tipo_entidad (descripcion) VALUES ('Persona natural'), ('Persona juridica');
INSERT INTO Medio_pago (descripcion) VALUES ('Efectivo'), ('Tarjeta'), ('Transferencia');
INSERT INTO Tipo_documento (descripcion) VALUES ('CC'), ('CE'), ('NIT');

INSERT INTO Codigo_postal (id_codigo_postal, pais, departamento, ciudad) VALUES
('110111', 'Colombia', 'Cundinamarca', 'Bogotá'),
('760001', 'Colombia', 'Valle del Cauca', 'Cali'),
('050001', 'Colombia', 'Antioquia', 'Medellín'),
('680001', 'Colombia', 'Santander', 'Bucaramanga'),
('190001', 'Colombia', 'Cauca', 'Popayán'),
('170001', 'Colombia', 'Caldas', 'Manizales'),
('200001', 'Colombia', 'Cesar', 'Valledupar'),
('180001', 'Colombia', 'Caquetá', 'Florencia'),
('440001', 'Colombia', 'La Guajira', 'Riohacha'),
('810001', 'Colombia', 'Arauca', 'Arauca'),
('520001', 'Colombia', 'Nariño', 'Pasto'),
('410001', 'Colombia', 'Huila', 'Neiva'),
('230001', 'Colombia', 'Córdoba', 'Montería'),
('730001', 'Colombia', 'Tolima', 'Ibagué'),
('630001', 'Colombia', 'Quindío', 'Armenia'),
('500001', 'Colombia', 'Meta', 'Villavicencio'),
('880001', 'Colombia', 'San Andrés y Providencia', 'San Andrés'),
('810010', 'Colombia', 'Arauca', 'Tame'),
('540001', 'Colombia', 'Norte de Santander', 'Cúcuta'),
('860001', 'Colombia', 'Putumayo', 'Mocoa'),
('270001', 'Colombia', 'Chocó', 'Quibdó'),
('660001', 'Colombia', 'Risaralda', 'Pereira'),
('850001', 'Colombia', 'Casanare', 'Yopal'),
('470001', 'Colombia', 'Magdalena', 'Santa Marta'),
('760033', 'Colombia', 'Valle del Cauca', 'Yumbo'),
('250001', 'Colombia', 'Cundinamarca', 'Soacha'),
('150001', 'Colombia', 'Boyacá', 'Tunja'),
('680005', 'Colombia', 'Santander', 'Floridablanca'),
('730006', 'Colombia', 'Tolima', 'Espinal'),
('130001', 'Colombia', 'Bolívar', 'Cartagena');

INSERT INTO Categoria_licencia (descripcion) VALUES
('A1'),
('A2'),
('B1'),
('B2'),
('C1'),
('C2'),
('C3'),
('D1'),
('D2'),
('E1');

INSERT INTO Tipo_mantenimiento (descripcion) VALUES ('Preventivo'), ('Correctivo');

INSERT INTO Taller_mantenimiento (nombre, direccion, telefono) VALUES ('Taller Central', 'Cra 10 #20-30, Bogotá', '3101234567');

INSERT INTO Estado_vehiculo (descripcion) VALUES ('Disponible'), ('En mantenimiento');

INSERT INTO Marca_vehiculo (nombre_marca) VALUES
('Renault'),
('Chevrolet'),
('Mazda'),
('Hyundai'),
('Kia'),
('Toyota'),
('Nissan'),
('Volkswagen'),
('Ford'),
('Suzuki'),
('Mitsubishi'),
('Peugeot');

INSERT INTO Color_vehiculo (nombre_color) VALUES
('Blanco'),
('Negro'),
('Rojo'),
('Gris'),
('Plateado'),
('Azul'),
('Verde'),
('Beige'),
('Amarillo'),
('Café'),
('Vino Tinto'),
('Naranja');

INSERT INTO Tipo_vehiculo (descripcion, capacidad, combustible, tarifa_dia) VALUES
('Sedán', 5, 'Gasolina', 120000),
('SUV', 7, 'Diesel', 180000),
('Pickup', 5, 'Diesel', 200000),
('Hatchback', 5, 'Gasolina', 100000),
('Convertible', 4, 'Gasolina', 220000),
('Camioneta', 7, 'Gasolina', 190000),
('Coupé', 4, 'Gasolina', 160000),
('Minivan', 8, 'Gasolina', 210000),
('4x4', 5, 'Diesel', 230000),
('Eléctrico', 5, 'Eléctrico', 150000),
('Híbrido', 5, 'Híbrido', 170000);

INSERT INTO Blindaje_vehiculo (descripcion) VALUES
('Ninguno'),
('Nivel 1'),
('Nivel 2'),
('Nivel 3'),
('Nivel 4'),
('Nivel 5'),
('Nivel 6'),
('Nivel 7'),
('Nivel 8'),
('Nivel 9'),
('Nivel 10');

INSERT INTO Transmision_vehiculo (descripcion) VALUES
('Manual'),
('Automática'),
('Semi-Automática'),
('Doble embrague'),
('Secuencial');

INSERT INTO Cilindraje_vehiculo (descripcion) VALUES
('1000cc'),
('1200cc'),
('1400cc'),
('1600cc'),
('1800cc'),
('2000cc'),
('2200cc'),
('2400cc'),
('3000cc'),
('3500cc'),
('4000cc');

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
('Vigente', 'Todo riesgo', '2025-12-31', 300000),
('Vencido', 'SOAT', '2024-05-15', 140000),
('Vigente', 'Responsabilidad civil', '2026-03-10', 180000),
('Próximo a vencer', 'SOAT', '2025-07-30', 155000),
('Vigente', 'Robo total', '2026-01-20', 250000),
('Vigente', 'Daños a terceros', '2025-11-15', 190000),
('Vigente', 'Todo riesgo', '2026-02-28', 320000),
('Vencido', 'Robo parcial', '2023-12-31', 130000),
('Próximo a vencer', 'Todo riesgo', '2025-08-15', 295000);

-- Vehículos de prueba
INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_blindaje, id_transmision, id_cilindraje, id_seguro_vehiculo, id_estado_vehiculo, id_proveedor, id_sucursal)
VALUES
('ABC123', 'CHS123456', 'Logan 2020', 25000, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1),
('XYZ789', 'CHS654321', 'Captiva 2022', 12000, 2, 2, 2, 2, 1, 2, 2, 1, 1, 1);

-- Seguros de alquiler
INSERT INTO Seguro_alquiler (estado, descripcion, vencimiento, costo) VALUES
('Vigente', 'Seguro todo riesgo', '2025-12-31', 50000),
('Vigente', 'Seguro básico', '2025-12-31', 20000),
('Vencido', 'Seguro contra robo', '2024-11-15', 30000),
('Vigente', 'Seguro por colisión', '2026-01-20', 40000),
('Próximo a vencer', 'Seguro todo riesgo', '2025-08-01', 52000),
('Vigente', 'Seguro daños a terceros', '2025-10-10', 35000),
('Vigente', 'Seguro extendido', '2026-03-05', 60000),
('Vencido', 'Seguro básico', '2024-06-30', 18000),
('Próximo a vencer', 'Seguro contra robo', '2025-07-30', 32000),
('Vigente', 'Seguro combinado', '2026-04-15', 55000),
('Sin seguro', 'Ninguno', NULL, 0);

-- Descuentos de alquiler
INSERT INTO Descuento_alquiler (descripcion, valor, fecha_inicio, fecha_fin) VALUES
('Sin descuento', 0, '2024-01-01 00:00:00', '2030-12-31 23:59:59'),
('Promoción fin de semana', 40000, '2025-07-01 00:00:00', '2025-07-31 23:59:59'),
('Descuento navideño', 50000, '2025-12-01 00:00:00', '2025-12-31 23:59:59'),
('Promoción Semana Santa', 30000, '2025-04-10 00:00:00', '2025-04-20 23:59:59'),
('Promoción aniversario', 55000, '2025-08-01 00:00:00', '2025-08-15 23:59:59');


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
INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva, id_alquiler, id_empleado)
VALUES
    ('2024-05-30 09:00:00', 100000, 110000, 1, 1, 3),
    ('2024-06-08 08:00:00', 50000, 150000, 1, 2, 4),
    ('2024-07-04 07:00:00', 60000, 90000, 1, 3, 4),
    ('2024-07-11 14:00:00', 70000, 100000, 1, 4, 3),
    ('2024-07-18 10:00:00', 90000, 100000, 1, 5, 3),
    ('2024-08-01 12:00:00', 75000, 175000, 1, 6, 4),
    ('2024-08-14 13:00:00', 70000, 160000, 1, 7, 3);

-- Abonos a reservas
INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) VALUES
    (100000, '2024-05-30 10:00:00', 1, 1),
    (50000, '2024-06-08 09:00:00', 2, 2),
    (60000, '2024-07-04 08:00:00', 3, 1),
    (70000, '2024-07-11 15:00:00', 4, 2),
    (90000, '2024-07-18 11:00:00', 5, 1),
    (75000, '2024-08-01 13:00:00', 6, 2),
    (70000, '2024-08-14 14:00:00', 7, 1);
