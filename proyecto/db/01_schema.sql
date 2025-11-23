DROP DATABASE IF EXISTS reservas_db;
CREATE DATABASE reservas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE reservas_db;

-- TABLA 1: LOGIN
CREATE TABLE login (
    correo VARCHAR(100) PRIMARY KEY,
    contrasena VARCHAR(255) NOT NULL
);

-- TABLA 2: PARTICIPANTE
CREATE TABLE participante (
    ci VARCHAR(20)  PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    rol_sistema ENUM('admin', 'usuario') DEFAULT 'usuario',  
    FOREIGN KEY (email) REFERENCES login(correo) ON DELETE CASCADE
);

-- TABLA 3: FACULTAD
CREATE TABLE facultad (
    id_facultad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- TABLA 4: PROGRAMA_ACADEMICO
CREATE TABLE programa_academico (
    nombre_programa VARCHAR(100) PRIMARY KEY,
    id_facultad INT NOT NULL,
    tipo ENUM('grado', 'posgrado') NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);

-- TABLA 5: PARTICIPANTE_PROGRAMA_ACADEMICO
CREATE TABLE participante_programa_academico (
    id_alumno_programa INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(100) NOT NULL,
    rol_academico ENUM('alumno', 'docente') NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci) ON DELETE CASCADE,
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa)
);

-- TABLA 6: EDIFICIO DE LA UNIVERSIDAD
CREATE TABLE edificio (
    nombre_edificio VARCHAR(100) PRIMARY KEY,
    direccion VARCHAR(200) NOT NULL,
    departamento VARCHAR(100) NOT NULL
);

-- TABLA 7: SALA DE ESTUDIO
CREATE TABLE sala (
    nombre_sala VARCHAR(100) NOT NULL,
    edificio VARCHAR(100) NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre', 'docente', 'posgrado') NOT NULL,
    PRIMARY KEY (nombre_sala, edificio),
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio) ON DELETE CASCADE
);

-- TABLA 8: TURNO
CREATE TABLE turno (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

-- TABLA 9: RESERVAS DE SALAS
CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sala VARCHAR(100) NOT NULL,
    edificio VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    hora_inicio_rango TIME NULL,
    hora_fin_rango TIME NULL,
    estado ENUM('activa', 'cancelada', 'sin asistencia', 'finalizada') NOT NULL DEFAULT 'activa',
    FOREIGN KEY (nombre_sala, edificio) REFERENCES sala(nombre_sala, edificio),
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
);

-- TABLA 10: RESERVA_PARTICIPANTE
CREATE TABLE reserva_participante (
    ci_participante VARCHAR(20) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud_reserva DATE NOT NULL,
    asistencia BOOLEAN NOT NULL DEFAULT 0,
    nombre_invitado VARCHAR(100) NULL,
    apellido_invitado VARCHAR(100) NULL,
    PRIMARY KEY (id_reserva, ci_participante),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva) ON DELETE CASCADE
);

-- TABLA 11: SANCION_PARTICIPANTE
CREATE TABLE sancion_participante (
    id_sancion INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR (20) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci) ON DELETE CASCADE
);
-- USUARIO DE APLICACIÓN
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppass';
GRANT ALL PRIVILEGES ON reservas_db.* TO 'appuser'@'%';
FLUSH PRIVILEGES;