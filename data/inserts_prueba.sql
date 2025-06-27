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

-- Tipos de empleado (jerarquía)
INSERT INTO Tipo_empleado (descripcion) VALUES ('admin'), ('gerente'), ('ventas'), ('caja'), ('mantenimiento');

-- Empleados de cada tipo
INSERT INTO Empleado (documento, nombre, salario, cargo, telefono, direccion, correo, id_tipo_documento, id_tipo_empleado) VALUES
('100000001', 'Admin Principal', 5000000, 'Administrador', '3000000001', 'Calle 1 #1-01', 'admin@email.com', 1, 1),
('100000002', 'Gerente General', 4000000, 'Gerente', '3000000002', 'Calle 2 #2-02', 'gerente@email.com', 1, 2),
('100000003', 'Vendedor Uno', 2500000, 'Ventas', '3000000003', 'Calle 3 #3-03', 'ventas@email.com', 1, 3),
('100000004', 'Cajero Uno', 2200000, 'Caja', '3000000004', 'Calle 4 #4-04', 'caja@email.com', 1, 4),
('100000005', 'Mantenimiento Uno', 2300000, 'Mantenimiento', '3000000005', 'Calle 5 #5-05', 'mantenimiento@email.com', 1, 5);
