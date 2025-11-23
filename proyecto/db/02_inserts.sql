SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = 'utf8mb4_general_ci';

-- INSERT para tabla login
INSERT INTO login (correo, contrasena) VALUES
('admin@gmail.com', '$2b$12$waLY17SZQVVWEzBIPzY4cO74sBlDQgt41bjV7bUSpKXi9MUqc/GKC'),
('juan.perez@universidad.edu.uy', 'Pass123!'),
('maria.gonzalez@universidad.edu.uy', 'Secure456'),
('carlos.rodriguez@universidad.edu.uy', 'MyPass789'),
('ana.martinez@universidad.edu.uy', 'Ana2024!'),
('pedro.sanchez@universidad.edu.uy', 'Pedro@123'),
('lucia.fernandez@universidad.edu.uy', 'Lucia456!'),
('diego.lopez@universidad.edu.uy', 'Diego789'),
('sofia.garcia@universidad.edu.uy', 'Sofia@2024'),
('martin.diaz@universidad.edu.uy', 'Martin123'),
('valentina.ruiz@universidad.edu.uy', 'Vale456!');

-- INSERT para tabla participante
INSERT INTO participante (ci, nombre, apellido, email, rol_sistema) VALUES
('99999999', 'Administrador', 'Sistema', 'admin@gmail.com', 'admin'),
('12345678', 'Juan', 'Pérez', 'juan.perez@universidad.edu.uy', 'usuario'),
('23456789', 'María', 'González', 'maria.gonzalez@universidad.edu.uy', 'usuario'),
('34567890', 'Carlos', 'Rodríguez', 'carlos.rodriguez@universidad.edu.uy', 'usuario'),
('45678901', 'Ana', 'Martínez', 'ana.martinez@universidad.edu.uy', 'usuario'),
('56789012', 'Pedro', 'Sánchez', 'pedro.sanchez@universidad.edu.uy', 'usuario'),
('67890123', 'Lucía', 'Fernández', 'lucia.fernandez@universidad.edu.uy', 'usuario'),
('78901234', 'Diego', 'López', 'diego.lopez@universidad.edu.uy', 'usuario'),
('89012345', 'Sofía', 'García', 'sofia.garcia@universidad.edu.uy', 'usuario'),
('90123456', 'Martín', 'Díaz', 'martin.diaz@universidad.edu.uy', 'usuario'),
('11223344', 'Valentina', 'Ruiz', 'valentina.ruiz@universidad.edu.uy', 'usuario');

-- INSERT para tabla facultad
INSERT INTO facultad (id_facultad, nombre) VALUES
(1, 'Facultad de Ingeniería'),
(2, 'Facultad de Medicina'),
(3, 'Facultad de Derecho'),
(4, 'Facultad de Ciencias Económicas'),
(5, 'Facultad de Ciencias'),
(6, 'Facultad de Humanidades'),
(7, 'Facultad de Arquitectura'),
(8, 'Facultad de Psicología'),
(9, 'Facultad de Veterinaria'),
(10, 'Facultad de Agronomía');

-- INSERT para tabla programa_academico
INSERT INTO programa_academico (nombre_programa, id_facultad, tipo) VALUES
('Ingeniería en Sistemas', 1, 'grado'),
('Medicina General', 2, 'grado'),
('Derecho', 3, 'grado'),
('Contador Público', 4, 'grado'),
('Licenciatura en Física', 5, 'grado'),
('Maestría en Ingeniería', 1, 'posgrado'),
('Especialización Médica', 2, 'posgrado'),
('Maestría en Derecho Penal', 3, 'posgrado'),
('Doctorado en Economía', 4, 'posgrado'),
('Maestría en Matemáticas', 5, 'posgrado');

-- INSERT para tabla participante_programa_academico
INSERT INTO participante_programa_academico (ci_participante, nombre_programa, rol_academico) VALUES
('12345678', 'Ingeniería en Sistemas', 'alumno'),
('23456789', 'Medicina General', 'alumno'),
('34567890', 'Derecho', 'docente'),
('45678901', 'Contador Público', 'alumno'),
('56789012', 'Licenciatura en Física', 'docente'),
('67890123', 'Maestría en Ingeniería', 'alumno'),
('78901234', 'Especialización Médica', 'alumno'),
('89012345', 'Maestría en Derecho Penal', 'docente'),
('90123456', 'Doctorado en Economía', 'alumno'),
('11223344', 'Maestría en Matemáticas', 'alumno');

-- INSERT para tabla edificio
INSERT INTO edificio (nombre_edificio, direccion, departamento) VALUES
('Edificio Central', 'Av. 18 de Julio 1234', 'Montevideo'),
('Edificio Norte', 'Bulevar Artigas 567', 'Montevideo'),
('Edificio Sur', 'Av. Italia 890', 'Montevideo'),
('Edificio Este', 'Av. Rivera 2345', 'Montevideo'),
('Edificio Oeste', 'Av. Agraciada 678', 'Montevideo'),
('Campus Salto', 'Uruguay 123', 'Salto'),
('Campus Maldonado', 'Rambla 456', 'Maldonado'),
('Edificio Ciencias', 'Iguá 789', 'Montevideo'),
('Edificio Posgrado', 'Dr. Tristán Narvaja 1011', 'Montevideo'),
('Anexo A', 'Colonia 1213', 'Montevideo');

-- INSERT para tabla sala
INSERT INTO sala (nombre_sala, edificio, capacidad, tipo_sala) VALUES
('Sala 101', 'Edificio Central', 30, 'libre'),
('Sala 202', 'Edificio Norte', 50, 'docente'),
('Sala 303', 'Edificio Sur', 25, 'libre'),
('Sala 404', 'Edificio Este', 40, 'posgrado'),
('Sala 505', 'Edificio Oeste', 35, 'libre'),
('Aula Magna', 'Campus Salto', 100, 'docente'),
('Sala 201', 'Campus Maldonado', 30, 'libre'),
('Laboratorio A', 'Edificio Ciencias', 20, 'docente'),
('Sala Seminario', 'Edificio Posgrado', 15, 'posgrado'),
('Sala 102', 'Anexo A', 45, 'libre');

-- INSERT para tabla turno 
INSERT INTO turno (id_turno, hora_inicio, hora_fin) VALUES
(1, '08:00:00', '09:00:00'),
(2, '09:00:00', '10:00:00'),
(3, '10:00:00', '11:00:00'),
(4, '11:00:00', '12:00:00'),
(5, '12:00:00', '13:00:00'),
(6, '13:00:00', '14:00:00'),
(7, '14:00:00', '15:00:00'),
(8, '15:00:00', '16:00:00'),
(9, '16:00:00', '17:00:00'),
(10, '17:00:00', '18:00:00'),
(11, '18:00:00', '19:00:00'),
(12, '19:00:00', '20:00:00'),
(13, '20:00:00', '21:00:00'),
(14, '21:00:00', '22:00:00'),
(15, '22:00:00', '23:00:00');

-- INSERT para tabla reserva
INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado) VALUES
('Sala 101', 'Edificio Central', '2024-11-15', 1, 'activa'),
('Sala 202', 'Edificio Norte', '2024-11-16', 2, 'activa'),
('Sala 303', 'Edificio Sur', '2024-11-17', 3, 'finalizada'),
('Sala 404', 'Edificio Este', '2024-11-18', 4, 'activa'),
('Sala 505', 'Edificio Oeste', '2024-11-19', 5, 'cancelada'),
('Aula Magna', 'Campus Salto', '2024-11-20', 6, 'activa'),
('Sala 201', 'Campus Maldonado', '2024-11-21', 7, 'sin asistencia'),
('Laboratorio A', 'Edificio Ciencias', '2024-11-22', 8, 'finalizada'),
('Sala Seminario', 'Edificio Posgrado', '2024-11-23', 9, 'activa'),
('Sala 102', 'Anexo A', '2024-11-24', 10, 'activa');

-- INSERT para tabla reserva_participante
INSERT INTO reserva_participante (ci_participante, id_reserva, fecha_solicitud_reserva, asistencia) VALUES
('12345678', 1, '2024-11-10', TRUE),
('23456789', 2, '2024-11-11', TRUE),
('34567890', 3, '2024-11-12', TRUE),
('45678901', 4, '2024-11-13', FALSE),
('56789012', 5, '2024-11-14', FALSE),
('67890123', 6, '2024-11-15', TRUE),
('78901234', 7, '2024-11-16', FALSE),
('89012345', 8, '2024-11-17', TRUE),
('90123456', 9, '2024-11-18', TRUE),
('11223344', 10, '2024-11-19', TRUE);

-- INSERT para tabla sancion_participante
INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin) VALUES
('45678901', '2024-11-01', '2024-11-08'),
('56789012', '2024-11-05', '2024-11-12'),
('78901234', '2024-11-10', '2024-11-17'),
('12345678', '2024-10-15', '2024-10-22'),
('23456789', '2024-10-20', '2024-10-27'),
('34567890', '2024-09-01', '2024-09-08'),
('67890123', '2024-09-10', '2024-09-17'),
('89012345', '2024-08-15', '2024-08-22'),
('90123456', '2024-08-20', '2024-08-27'),
('11223344', '2024-07-01', '2024-07-08');

