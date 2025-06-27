-- Crear roles
INSERT INTO Rol (nombre) VALUES ('cliente'), ('empleado'), ('gerente'), ('admin');

-- Tipos y catálogos
INSERT INTO Tipo_entidad (descripcion) VALUES ('Persona natural'), ('Empresa');
INSERT INTO Medio_pago (descripcion) VALUES ('Efectivo'), ('Tarjeta'), ('Transferencia');
INSERT INTO Tipo_cliente (descripcion) VALUES ('VIP'), ('Regular');
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

-- Sucursal y proveedor
INSERT INTO Sucursal (nombre, direccion, telefono, gerente, id_codigo_postal) VALUES ('Sucursal Norte', 'Av 68 #100-20, Bogotá', '3209876543', 'Ana Gerente', '110111');
INSERT INTO Proveedor_vehiculo (nombre, direccion, telefono, correo) VALUES ('Autocolombia', 'Calle 80 #30-15, Bogotá', '3152223344', 'ventas@autocolombia.com');

-- Licencia de conducción
INSERT INTO Licencia_conduccion (estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES ('Vigente', '2022-01-10', '2027-01-10', 1);

-- Clientes y empleados
INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, id_licencia, id_tipo_documento, id_tipo_cliente, id_codigo_postal) VALUES ('987654321', 'Carlos Ramírez', '3111111111', 'Calle 12 #34-56, Bogotá', 'carlos.ramirez@email.com', 1, 1, 2, '110111');
INSERT INTO Empleado (documento, nombre, salario, cargo, telefono, direccion, correo, id_tipo_documento) VALUES ('123456789', 'Elena Torres', 2500000, 'Asesor', '3122222222', 'Cra 15 #45-67, Bogotá', 'elena.torres@email.com', 1);

-- Vehículo y seguro
INSERT INTO Seguro_vehiculo (estado, descripcion, vencimiento, costo) VALUES ('Vigente', 'Todo riesgo', '2025-12-31', 900000);
INSERT INTO Vehiculo (placa, n_chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_blindaje, id_transmision, id_cilindraje, id_seguro_vehiculo, id_estado_vehiculo, id_proveedor, id_sucursal) VALUES ('ABC123', 'CHS123456789', '2022', 15000, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1);

-- 1. Insertar en Seguro_alquiler
INSERT INTO Seguro_alquiler (estado, descripcion, vencimiento, costo)
VALUES ('Vigente', 'Todo riesgo', '2025-12-31', 900000);

-- 2. Insertar en Reserva_alquiler
INSERT INTO Reserva_alquiler (fecha_hora, abono, saldo_pendiente, id_estado_reserva)
VALUES ('2024-07-01 09:00:00', 500000, 0, 1);

SET @id_reserva := LAST_INSERT_ID();

-- 3. Insertar en Alquiler (usando el id_seguro y el id_reserva correctos)
INSERT INTO Alquiler (fecha_hora_salida, fecha_hora_entrada, id_vehiculo, id_cliente, id_seguro, id_estado)
VALUES ('2024-07-01 09:00:00', '2024-07-05 18:00:00', 'ABC123', 1, 1, 1);

-- 4. Insertar en Abono_reserva (usando el id_reserva correcto y el id_medio_pago)
INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago)
VALUES (500000, '2024-07-01 10:00:00', @id_reserva, 1);
