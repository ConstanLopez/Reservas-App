from app.database import fetch_query

class Reportes:
    """
    Consultas de BI 
    """

    @staticmethod
    def salas_mas_reservadas(limit=10):
        """Salas con más reservas (ordenadas)"""
        query = """
            SELECT s.nombre_sala, s.edificio, s.tipo_sala, s.capacidad,
                   COUNT(r.id_reserva) as total_reservas
            FROM sala s
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            GROUP BY s.nombre_sala, s.edificio, s.tipo_sala, s.capacidad
            ORDER BY total_reservas DESC
            LIMIT %s
        """
        return fetch_query(query, (limit,))

    @staticmethod
    def turnos_mas_demandados():
        """Turnos con más reservas, se usa time format por un tema con timedelta de python, para que no de error"""
        query = """
            SELECT t.id_turno,
                   TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                   TIME_FORMAT(t.hora_fin, '%H:%i') AS hora_fin,
                   COUNT(r.id_reserva) as total_reservas
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
            GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
            ORDER BY total_reservas DESC
        """
        return fetch_query(query)

    @staticmethod
    def promedio_participantes_por_sala():
        """Promedio de participantes por sala"""
        query = """
            SELECT s.nombre_sala, s.edificio, s.capacidad,
                   COUNT(DISTINCT r.id_reserva) as total_reservas,
                   COUNT(rp.ci_participante) as total_participantes,
                   IFNULL(ROUND(COUNT(rp.ci_participante) / COUNT(DISTINCT r.id_reserva), 2), 0) as promedio_participantes
            FROM sala s
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            GROUP BY s.nombre_sala, s.edificio, s.capacidad
            ORDER BY promedio_participantes DESC
        """
        return fetch_query(query)

    @staticmethod
    def reservas_por_carrera_y_facultad():
        """Cantidad de reservas agrupadas por programa y facultad"""
        query = """
            SELECT f.nombre AS facultad,
                   pa.nombre_programa,
                   pa.tipo,
                   COUNT(DISTINCT r.id_reserva) AS total_reservas
            FROM facultad f
            JOIN programa_academico pa ON f.id_facultad = pa.id_facultad
            LEFT JOIN participante_programa_academico ppa ON pa.nombre_programa = ppa.nombre_programa
            LEFT JOIN reserva_participante rp ON ppa.ci_participante = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            GROUP BY f.nombre, pa.nombre_programa, pa.tipo
            ORDER BY f.nombre, total_reservas DESC
        """
        return fetch_query(query)

    @staticmethod
    def porcentaje_ocupacion_por_edificio():
        """Porcentaje de ocupación de salas por edificio"""
        query = """
            SELECT e.nombre_edificio,
                   COUNT(DISTINCT s.nombre_sala) AS total_salas,
                   COUNT(DISTINCT CASE WHEN r.estado = 'activa' THEN r.id_reserva END) AS reservas_activas,
                   COUNT(DISTINCT r.id_reserva) AS total_reservas,
                   IFNULL(ROUND((COUNT(DISTINCT r.id_reserva) * 100.0) / 
                                (COUNT(DISTINCT s.nombre_sala) * 15), 2), 0) AS porcentaje_ocupacion
            FROM edificio e
            JOIN sala s ON e.nombre_edificio = s.edificio
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            GROUP BY e.nombre_edificio
            ORDER BY porcentaje_ocupacion DESC
        """
        return fetch_query(query)

    @staticmethod
    def reservas_y_asistencias_por_rol():
        """Cantidad de reservas y asistencias separadas por rol académico"""
        query = """
            SELECT 
                ppa.rol_academico AS rol,
                pa.tipo AS tipo_programa,
                COUNT(DISTINCT r.id_reserva) AS total_reservas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) AS total_asistencias,
                SUM(CASE WHEN rp.asistencia = 0 AND r.estado = 'sin asistencia' THEN 1 ELSE 0 END) AS total_inasistencias,
                IFNULL(ROUND((SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) * 100.0) / 
                             COUNT(DISTINCT r.id_reserva), 2), 0) AS porcentaje_asistencia
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN reserva_participante rp ON ppa.ci_participante = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            GROUP BY ppa.rol_academico, pa.tipo
            ORDER BY ppa.rol_academico, pa.tipo
        """
        return fetch_query(query)

    @staticmethod
    def cantidad_sanciones_por_rol():
        """Cantidad de sanciones por rol académico"""
        query = """
            SELECT 
                ppa.rol_academico AS rol,
                pa.tipo AS tipo_programa,
                COUNT(DISTINCT s.id_sancion) AS total_sanciones,
                COUNT(DISTINCT CASE 
                    WHEN CURDATE() BETWEEN s.fecha_inicio AND s.fecha_fin 
                    THEN s.id_sancion 
                END) AS sanciones_activas
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN sancion_participante s ON ppa.ci_participante = s.ci_participante
            GROUP BY ppa.rol_academico, pa.tipo
            ORDER BY total_sanciones DESC
        """
        return fetch_query(query)

    @staticmethod
    def efectividad_reservas():
        """Porcentaje de reservas utilizadas vs canceladas/no asistidas"""
        query = """
            SELECT 
                COUNT(*) AS total_reservas,
                SUM(CASE WHEN estado = 'finalizada' THEN 1 ELSE 0 END) AS finalizadas,
                SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) AS canceladas,
                SUM(CASE WHEN estado = 'sin asistencia' THEN 1 ELSE 0 END) AS sin_asistencia,
                SUM(CASE WHEN estado = 'activa' THEN 1 ELSE 0 END) AS activas,
                ROUND((SUM(CASE WHEN estado = 'finalizada' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS porcentaje_utilizadas,
                ROUND((SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS porcentaje_canceladas,
                ROUND((SUM(CASE WHEN estado = 'sin asistencia' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS porcentaje_sin_asistencia
            FROM reserva
        """
        result = fetch_query(query)
        return result[0] if result else {}

    # CONSULTAS ADICIONALES
    @staticmethod
    def horarios_pico():
        """Horarios de mayor demanda"""
        query = """
            SELECT 
                CASE 
                    WHEN HOUR(t.hora_inicio) BETWEEN 8 AND 11 THEN 'Mañana (8-12)'
                    WHEN HOUR(t.hora_inicio) BETWEEN 12 AND 17 THEN 'Tarde (12-18)'
                    ELSE 'Noche (18-23)'
                END AS franja_horaria,
                COUNT(r.id_reserva) AS total_reservas,
                ROUND(COUNT(r.id_reserva) * 100.0 / (SELECT COUNT(*) FROM reserva), 2) AS porcentaje
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
            GROUP BY franja_horaria
            ORDER BY total_reservas DESC
        """
        return fetch_query(query)

    @staticmethod
    def tendencia_uso_mensual():
        """
        Consulta adicional: Tendencia de uso por mes (útil para planificación)
        Retorna cantidad de reservas, salas y edificios usados por mes.
        """
        query = """
            SELECT 
                DATE_FORMAT(fecha, '%Y-%m') AS mes,
                COUNT(*) AS total_reservas,
                COUNT(DISTINCT nombre_sala) AS salas_utilizadas,
                COUNT(DISTINCT edificio) AS edificios_utilizados
            FROM reserva
            WHERE estado IN ('activa', 'finalizada')
            GROUP BY mes
            ORDER BY mes ASC
        """
        return fetch_query(query)

    @staticmethod
    def ranking_usuarios_activos():
        """Top usuarios más activos"""
        query = """
            SELECT 
                p.ci,
                p.nombre,
                p.apellido,
                p.rol_sistema,
                ppa.rol_academico,
                pa.tipo AS tipo_programa,
                COUNT(DISTINCT r.id_reserva) AS total_reservas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) AS asistencias,
                COUNT(DISTINCT s.id_sancion) AS sanciones
            FROM participante p
            JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN reserva_participante rp ON p.ci = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            LEFT JOIN sancion_participante s ON p.ci = s.ci_participante
            GROUP BY p.ci, p.nombre, p.apellido, p.rol_sistema, ppa.rol_academico, pa.tipo
            HAVING total_reservas > 0
            ORDER BY total_reservas DESC
            LIMIT 20
        """
        return fetch_query(query)
