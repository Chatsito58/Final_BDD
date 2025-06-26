-- Crear roles
INSERT INTO Rol (nombre) VALUES ('cliente'), ('empleado');

-- Registrar un cliente y un empleado (solo datos obligatorios)
INSERT INTO Cliente (documento, nombre) VALUES ('987654321', 'Carlos Cliente');
INSERT INTO Empleado (documento, nombre) VALUES ('123456789', 'Elena Empleado');

-- Contraseñas en SHA-256
-- 'cliente123'  -> 09a31a7001e261ab1e056182a71d3cf57f582ca9a29cff5eb83be0f0549730a9
-- 'empleado123' -> ccc13e8ab0819e3ab61719de4071ecae6c1d3cd35dc48b91cad3481f20922f9f

-- Cuentas de usuario asociadas a cada rol
INSERT INTO Usuario (usuario, contrasena, id_rol, id_cliente)
VALUES ('cliente1',
        '09a31a7001e261ab1e056182a71d3cf57f582ca9a29cff5eb83be0f0549730a9',
        (SELECT id_rol FROM Rol WHERE nombre = 'cliente'),
        (SELECT id_cliente FROM Cliente WHERE documento = '987654321'));

INSERT INTO Usuario (usuario, contrasena, id_rol, id_empleado)
VALUES ('empleado1',
        'ccc13e8ab0819e3ab61719de4071ecae6c1d3cd35dc48b91cad3481f20922f9f',
        (SELECT id_rol FROM Rol WHERE nombre = 'empleado'),
        (SELECT id_empleado FROM Empleado WHERE documento = '123456789'));
