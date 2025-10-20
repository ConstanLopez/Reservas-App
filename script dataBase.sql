CREATE DATABASE reservas_db;
USE reservas_db;

CREATE TABLE login (
    correo VARCHAR(50) PRIMARY KEY ,
    contraseña VARCHAR(50) NOT NULL
);
CREATE TABLE participante (
    ci CHAR(8) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    FOREIGN KEY (email) REFERENCES login(correo)
);

CREATE TABLE facultad (
    id_facultad INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE programa_academico (
    nombre_programa VARCHAR(50) PRIMARY KEY ,
    id_facultad INT NOT NULL ,
    tipo ENUM('grado', 'posgrado') NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES  facultad(id_facultad)
);

CREATE TABLE participante_programa_academico (
    id_alumno_programa INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante CHAR(8) NOT NULL ,
    nombre_programa VARCHAR(50) NOT NULL,
    rol ENUM ('alumno', 'docente') NOT NULL,
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa),
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)

);

CREATE TABLE edificio (
    nombre_edificio VARCHAR (50) PRIMARY KEY,
    direccion VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL
);

CREATE TABLE sala (
    nombre_sala VARCHAR(50) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM ('libre', 'docente' , 'posgrado') NOT NULL,
    PRIMARY KEY (nombre_sala,edificio),
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);



CREATE TABLE turno(
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

CREATE TABLE reserva(
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sala VARCHAR(50) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    estado ENUM('activa', 'cancelada', 'sin asistencia', 'finalizada') NOT NULL,
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno),
    FOREIGN KEY (nombre_sala,edificio) REFERENCES sala(nombre_sala,edificio),
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);

CREATE TABLE reserva_participante (
    ci_participante CHAR (8) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud_reserva DATE NOT NULL,
    asistencia BOOLEAN NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
);

CREATE TABLE sancion_partcipante(
    ci_participante CHAR(8) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    PRIMARY KEY (ci_participante,fecha_inicio,fecha_fin)
);
