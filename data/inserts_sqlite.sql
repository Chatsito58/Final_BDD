-- Datos iniciales para SQLite - Base de datos Alquiler_vehiculos

-- Insertar tipos de entidad
INSERT OR IGNORE INTO Tipo_entidad (id_tipo_entidad, descripcion) VALUES 
(1, 'Cliente'),
(2, 'Proveedor'),
(3, 'Taller'),
(4, 'Sucursal');

-- Insertar medios de pago
INSERT OR IGNORE INTO Medio_pago (id_medio_pago, descripcion) VALUES 
(1, 'Efectivo'),
(2, 'Tarjeta de Crédito'),
(3, 'Tarjeta de Débito'),
(4, 'Transferencia Bancaria'),
(5, 'PSE');

-- Insertar tipos de documento
INSERT OR IGNORE INTO Tipo_documento (id_tipo_documento, descripcion) VALUES 
(1, 'Cédula de Ciudadanía'),
(2, 'Tarjeta de Identidad'),
(3, 'Cédula de Extranjería'),
(4, 'Pasaporte'),
(5, 'NIT');

-- Insertar códigos postales
INSERT OR IGNORE INTO Codigo_postal (id_codigo_postal, pais, departamento, ciudad) VALUES 
('11001', 'Colombia', 'Bogotá D.C.', 'Bogotá'),
('05001', 'Colombia', 'Antioquia', 'Medellín'),
('76001', 'Colombia', 'Valle del Cauca', 'Cali'),
('08001', 'Colombia', 'Atlántico', 'Barranquilla'),
('13001', 'Colombia', 'Bolívar', 'Cartagena');

-- Insertar categorías de licencia
INSERT OR IGNORE INTO Categoria_licencia (id_categoria, descripcion) VALUES 
(1, 'A1 - Motocicletas hasta 125cc'),
(2, 'A2 - Motocicletas hasta 250cc'),
(3, 'B1 - Automóviles particulares'),
(4, 'B2 - Camiones hasta 3.5 toneladas'),
(5, 'C1 - Camiones hasta 7.5 toneladas'),
(6, 'C2 - Camiones pesados');

-- Insertar tipos de mantenimiento
INSERT OR IGNORE INTO Tipo_mantenimiento (id_tipo, descripcion) VALUES 
(1, 'Mantenimiento Preventivo'),
(2, 'Mantenimiento Correctivo'),
(3, 'Cambio de Aceite'),
(4, 'Revisión Técnico Mecánica'),
(5, 'Reparación de Frenos'),
(6, 'Reparación de Motor');

-- Insertar talleres de mantenimiento
INSERT OR IGNORE INTO Taller_mantenimiento (id_taller, nombre, direccion, telefono) VALUES 
(1, 'Taller Central', 'Calle 123 #45-67, Bogotá', '601-1234567'),
(2, 'Taller Norte', 'Carrera 78 #90-12, Medellín', '604-2345678'),
(3, 'Taller Sur', 'Avenida 5 #23-45, Cali', '602-3456789'),
(4, 'Taller Este', 'Calle 10 #56-78, Barranquilla', '605-4567890');

-- Insertar estados de vehículo
INSERT OR IGNORE INTO Estado_vehiculo (id_estado, descripcion) VALUES 
(1, 'Disponible'),
(2, 'En Alquiler'),
(3, 'En Mantenimiento'),
(4, 'Fuera de Servicio'),
(5, 'Reservado');

-- Insertar marcas de vehículo
INSERT OR IGNORE INTO Marca_vehiculo (id_marca, nombre_marca) VALUES 
(1, 'Toyota'),
(2, 'Honda'),
(3, 'Ford'),
(4, 'Chevrolet'),
(5, 'Nissan'),
(6, 'Hyundai'),
(7, 'Kia'),
(8, 'Mazda'),
(9, 'Volkswagen'),
(10, 'BMW');

-- Insertar colores de vehículo
INSERT OR IGNORE INTO Color_vehiculo (id_color, nombre_color) VALUES 
(1, 'Blanco'),
(2, 'Negro'),
(3, 'Gris'),
(4, 'Plateado'),
(5, 'Azul'),
(6, 'Rojo'),
(7, 'Verde'),
(8, 'Amarillo'),
(9, 'Naranja'),
(10, 'Marrón');

-- Insertar tipos de vehículo
INSERT OR IGNORE INTO Tipo_vehiculo (id_tipo, descripcion, capacidad, combustible, tarifa_dia) VALUES 
(1, 'Sedán Económico', 5, 'Gasolina', 80000),
(2, 'Sedán Ejecutivo', 5, 'Gasolina', 120000),
(3, 'SUV Compacto', 5, 'Gasolina', 100000),
(4, 'SUV Familiar', 7, 'Gasolina', 140000),
(5, 'Camioneta', 8, 'Diesel', 160000),
(6, 'Deportivo', 2, 'Gasolina', 200000),
(7, 'Van', 12, 'Gasolina', 180000),
(8, 'Pickup', 5, 'Diesel', 150000);

-- Insertar tipos de blindaje
INSERT OR IGNORE INTO Blindaje_vehiculo (id_blindaje, descripcion) VALUES 
(1, 'Sin Blindaje'),
(2, 'Blindaje Nivel 1'),
(3, 'Blindaje Nivel 2'),
(4, 'Blindaje Nivel 3'),
(5, 'Blindaje Nivel 4');

-- Insertar tipos de transmisión
INSERT OR IGNORE INTO Transmision_vehiculo (id_transmision, descripcion) VALUES 
(1, 'Manual'),
(2, 'Automática'),
(3, 'CVT'),
(4, 'Semi-automática');

-- Insertar tipos de cilindraje
INSERT OR IGNORE INTO Cilindraje_vehiculo (id_cilindraje, descripcion) VALUES 
(1, '1000cc'),
(2, '1300cc'),
(3, '1500cc'),
(4, '1800cc'),
(5, '2000cc'),
(6, '2500cc'),
(7, '3000cc'),
(8, '3500cc'),
(9, '4000cc'),
(10, '5000cc');

-- Insertar estados de alquiler
INSERT OR IGNORE INTO Estado_alquiler (id_estado, descripcion) VALUES 
(1, 'Reservado'),
(2, 'En Curso'),
(3, 'Finalizado'),
(4, 'Cancelado'),
(5, 'Pendiente de Pago');

-- Insertar sucursales
INSERT OR IGNORE INTO Sucursal (id_sucursal, nombre, direccion, telefono, gerente, id_codigo_postal) VALUES 
(1, 'Sucursal Centro', 'Calle 15 #23-45, Bogotá', '601-1111111', 'Juan Pérez', '11001'),
(2, 'Sucursal Norte', 'Carrera 50 #80-90, Medellín', '604-2222222', 'María García', '05001'),
(3, 'Sucursal Sur', 'Avenida 4 #12-34, Cali', '602-3333333', 'Carlos López', '76001'),
(4, 'Sucursal Este', 'Calle 20 #45-67, Barranquilla', '605-4444444', 'Ana Rodríguez', '08001');

-- Insertar tipos de empleado
INSERT OR IGNORE INTO Tipo_empleado (id_tipo_empleado, descripcion) VALUES 
(1, 'Administrador'),
(2, 'Gerente'),
(3, 'Empleado'),
(4, 'Mecánico'),
(5, 'Conductor');

-- Insertar empleados de ejemplo
INSERT OR IGNORE INTO Empleado (id_empleado, documento, nombre, salario, cargo, telefono, direccion, correo, id_sucursal, id_tipo_documento, id_tipo_empleado) VALUES 
(1, '12345678', 'Juan Pérez', 2500000, 'Gerente', '300-1111111', 'Calle 10 #20-30, Bogotá', 'juan.perez@empresa.com', 1, 1, 2),
(2, '87654321', 'María García', 2200000, 'Gerente', '300-2222222', 'Carrera 40 #50-60, Medellín', 'maria.garcia@empresa.com', 2, 1, 2),
(3, '11223344', 'Carlos López', 2000000, 'Empleado', '300-3333333', 'Avenida 5 #15-25, Cali', 'carlos.lopez@empresa.com', 3, 1, 3),
(4, '44332211', 'Ana Rodríguez', 1800000, 'Empleado', '300-4444444', 'Calle 25 #35-45, Barranquilla', 'ana.rodriguez@empresa.com', 4, 1, 3);

-- Insertar licencias de conducción
INSERT OR IGNORE INTO Licencia_conduccion (id_licencia, estado, fecha_emision, fecha_vencimiento, id_categoria) VALUES 
(1, 'Vigente', '2020-01-15', '2030-01-15', 3),
(2, 'Vigente', '2019-03-20', '2029-03-20', 3),
(3, 'Vigente', '2021-06-10', '2031-06-10', 3),
(4, 'Vigente', '2018-11-05', '2028-11-05', 3);

-- Insertar clientes de ejemplo
INSERT OR IGNORE INTO Cliente (id_cliente, documento, nombre, telefono, direccion, correo, infracciones, id_licencia, id_tipo_documento, id_codigo_postal) VALUES 
(1, '98765432', 'Pedro Martínez', '300-5555555', 'Calle 30 #40-50, Bogotá', 'pedro.martinez@email.com', 0, 1, 1, '11001'),
(2, '56789012', 'Laura Silva', '300-6666666', 'Carrera 60 #70-80, Medellín', 'laura.silva@email.com', 1, 2, 1, '05001'),
(3, '34567890', 'Roberto Torres', '300-7777777', 'Avenida 8 #18-28, Cali', 'roberto.torres@email.com', 0, 3, 1, '76001'),
(4, '23456789', 'Carmen Vega', '300-8888888', 'Calle 35 #45-55, Barranquilla', 'carmen.vega@email.com', 2, 4, 1, '08001');

-- Insertar seguros de vehículo
INSERT OR IGNORE INTO Seguro_vehiculo (id_seguro, estado, descripcion, vencimiento, costo) VALUES 
(1, 'Vigente', 'Seguro Todo Riesgo', '2024-12-31', 500000),
(2, 'Vigente', 'Seguro Básico', '2024-12-31', 300000),
(3, 'Vigente', 'Seguro Premium', '2024-12-31', 800000),
(4, 'Vigente', 'Seguro Empresarial', '2024-12-31', 600000);

-- Insertar proveedores de vehículo
INSERT OR IGNORE INTO Proveedor_vehiculo (id_proveedor, nombre, direccion, telefono, correo) VALUES 
(1, 'Concesionario Central', 'Calle 100 #200-300, Bogotá', '601-9999999', 'info@concesionario.com'),
(2, 'Importadora Norte', 'Carrera 80 #90-100, Medellín', '604-8888888', 'ventas@importadora.com'),
(3, 'Distribuidora Sur', 'Avenida 10 #20-30, Cali', '602-7777777', 'contacto@distribuidora.com'),
(4, 'Comercial Este', 'Calle 50 #60-70, Barranquilla', '605-6666666', 'info@comercial.com');

-- Insertar vehículos de ejemplo
INSERT OR IGNORE INTO Vehiculo (placa, n_chasis, modelo, kilometraje, id_marca, id_color, id_tipo_vehiculo, id_blindaje, id_transmision, id_cilindraje, id_seguro_vehiculo, id_estado_vehiculo, id_proveedor, id_sucursal) VALUES 
('ABC123', 'CHS001', 'Corolla', 50000, 1, 1, 1, 1, 2, 4, 1, 1, 1, 1),
('DEF456', 'CHS002', 'Civic', 35000, 2, 2, 1, 1, 2, 4, 2, 1, 2, 2),
('GHI789', 'CHS003', 'Focus', 42000, 3, 3, 2, 1, 2, 5, 1, 1, 3, 3),
('JKL012', 'CHS004', 'Spark', 28000, 4, 4, 1, 1, 1, 2, 2, 1, 4, 4),
('MNO345', 'CHS005', 'Sentra', 65000, 5, 5, 2, 1, 2, 4, 1, 1, 1, 1),
('PQR678', 'CHS006', 'Accent', 38000, 6, 6, 1, 1, 1, 3, 2, 1, 2, 2),
('STU901', 'CHS007', 'Rio', 45000, 7, 7, 1, 1, 2, 3, 1, 1, 3, 3),
('VWX234', 'CHS008', '3', 52000, 8, 8, 2, 1, 2, 4, 2, 1, 4, 4);

-- Insertar seguros de alquiler
INSERT OR IGNORE INTO Seguro_alquiler (id_seguro, estado, descripcion, vencimiento, costo) VALUES 
(1, 'Vigente', 'Seguro Básico de Alquiler', '2024-12-31', 25000),
(2, 'Vigente', 'Seguro Completo de Alquiler', '2024-12-31', 50000),
(3, 'Vigente', 'Seguro Premium de Alquiler', '2024-12-31', 75000),
(4, 'Vigente', 'Seguro Empresarial de Alquiler', '2024-12-31', 100000);

-- Insertar descuentos de alquiler
INSERT OR IGNORE INTO Descuento_alquiler (id_descuento, descripcion, valor, fecha_inicio, fecha_fin) VALUES 
(1, 'Descuento por Semana', 10.0, '2024-01-01', '2024-12-31'),
(2, 'Descuento por Mes', 15.0, '2024-01-01', '2024-12-31'),
(3, 'Descuento Cliente Frecuente', 5.0, '2024-01-01', '2024-12-31'),
(4, 'Descuento Promocional', 20.0, '2024-06-01', '2024-08-31');

-- Insertar estados de reserva
INSERT OR IGNORE INTO Estado_reserva (id_estado, descripcion) VALUES 
(1, 'Pendiente'),
(2, 'Confirmada'),
(3, 'Cancelada'),
(4, 'Completada'),
(5, 'En Proceso');

-- Insertar roles (ya están en el schema, pero por si acaso)
INSERT OR IGNORE INTO Rol (id_rol, nombre) VALUES 
(1, 'cliente'),
(2, 'empleado'),
(3, 'gerente'),
(4, 'admin');
