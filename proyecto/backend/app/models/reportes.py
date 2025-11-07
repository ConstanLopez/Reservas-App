from app.database import fetch_query

class Reportes:
    """
    Consultas de Business Intelligence según especificaciones del obligatorio.
    """
    
    @staticmethod
    def salas_mas_reservadas(limit=10):
        """Salas con más reservas (ordenadas)"""
        query = """
            SELECT s.nombre_sala, s.edificio, s.tipo_sala, s.capacidad,
                   COUNT(r.id_reserva) as total_reservas
            FROM sala s
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            GROUP BY s.nombre_sala, s.edificio
            ORDER BY total_reservas DESC
            LIMIT %s
        """
        return fetch_query(query, (limit,))
    
    @staticmethod
    def turnos_mas_demandados():
        """Turnos con más reservas"""
        query = """
            SELECT t.id_turno, t.hora_inicio, t.hora_fin,
                   COUNT(r.id_reserva) as total_reservas
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
            GROUP BY t.id_turno
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
            GROUP BY s.nombre_sala, s.edificio
            ORDER BY promedio_participantes DESC
        """
        return fetch_query(query)
    
    @staticmethod
    def reservas_por_carrera_y_facultad():
        """Cantidad de reservas agrupadas por programa y facultad"""
        query = """
            SELECT f.nombre as facultad,
                   pa.nombre_programa,
                   pa.tipo,
                   COUNT(DISTINCT r.id_reserva) as total_reservas
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
                   COUNT(DISTINCT s.nombre_sala) as total_salas,
                   COUNT(DISTINCT CASE WHEN r.estado = 'activa' THEN r.id_reserva END) as reservas_activas,
                   COUNT(DISTINCT r.id_reserva) as total_reservas,
                   IFNULL(ROUND((COUNT(DISTINCT r.id_reserva) * 100.0) / 
                                (COUNT(DISTINCT s.nombre_sala) * 15), 2), 0) as porcentaje_ocupacion
            FROM edificio e
            JOIN sala s ON e.nombre_edificio = s.edificio
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            GROUP BY e.nombre_edificio
            ORDER BY porcentaje_ocupacion DESC
        """
        return fetch_query(query)
    
    @staticmethod
    def reservas_y_asistencias_por_rol():
        """Cantidad de reservas y asistencias separadas por rol (profesor/alumno grado/posgrado)"""
        query = """
            SELECT 
                ppa.rol,
                pa.tipo as tipo_programa,
                COUNT(DISTINCT r.id_reserva) as total_reservas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) as total_asistencias,
                SUM(CASE WHEN rp.asistencia = 0 AND r.estado = 'sin asistencia' THEN 1 ELSE 0 END) as total_inasistencias,
                IFNULL(ROUND((SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) * 100.0) / 
                             COUNT(DISTINCT r.id_reserva), 2), 0) as porcentaje_asistencia
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN reserva_participante rp ON ppa.ci_participante = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            GROUP BY ppa.rol, pa.tipo
            ORDER BY ppa.rol, pa.tipo
        """
        return fetch_query(query)
    
    @staticmethod
    def cantidad_sanciones_por_rol():
        """Cantidad de sanciones por rol (profesor/alumno)"""
        query = """
            SELECT 
                ppa.rol,
                pa.tipo as tipo_programa,
                COUNT(DISTINCT s.id_sancion) as total_sanciones,
                COUNT(DISTINCT CASE 
                    WHEN CURDATE() BETWEEN s.fecha_inicio AND s.fecha_fin 
                    THEN s.id_sancion 
                END) as sanciones_activas
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN sancion_participante s ON ppa.ci_participante = s.ci_participante
            GROUP BY ppa.rol, pa.tipo
            ORDER BY total_sanciones DESC
        """
        return fetch_query(query)
    
    @staticmethod
    def efectividad_reservas():
        """Porcentaje de reservas utilizadas vs canceladas/no asistidas"""
        query = """
            SELECT 
                COUNT(*) as total_reservas,
                SUM(CASE WHEN estado = 'finalizada' THEN 1 ELSE 0 END) as finalizadas,
                SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
                SUM(CASE WHEN estado = 'sin asistencia' THEN 1 ELSE 0 END) as sin_asistencia,
                SUM(CASE WHEN estado = 'activa' THEN 1 ELSE 0 END) as activas,
                ROUND((SUM(CASE WHEN estado = 'finalizada' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) as porcentaje_utilizadas,
                ROUND((SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) as porcentaje_canceladas,
                ROUND((SUM(CASE WHEN estado = 'sin asistencia' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) as porcentaje_sin_asistencia
            FROM reserva
        """
        result = fetch_query(query)
        return result[0] if result else {}
    
    # ========================================
    # CONSULTAS ADICIONALES (3 sugeridas)
    # ========================================
    
    @staticmethod
    def horarios_pico():
        """
        Consulta adicional 1: Identifica los horarios pico (mayor demanda por franja horaria)
        """
        query = """
            SELECT 
                CASE 
                    WHEN HOUR(t.hora_inicio) BETWEEN 8 AND 11 THEN 'Mañana (8-12)'
                    WHEN HOUR(t.hora_inicio) BETWEEN 12 AND 17 THEN 'Tarde (12-18)'
                    ELSE 'Noche (18-23)'
                END as franja_horaria,
                COUNT(r.id_reserva) as total_reservas,
                ROUND(COUNT(r.id_reserva) * 100.0 / (SELECT COUNT(*) FROM reserva), 2) as porcentaje
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
            GROUP BY franja_horaria
            ORDER BY total_reservas DESC
        """
        return fetch_query(query)
    
    @staticmethod
    def tendencia_uso_mensual():
        """
        Consulta adicional 2: Tendencia de uso por mes (útil para planificación)
        """
        query = """
            SELECT 
                DATE_FORMAT(fecha, '%Y-%m') as mes,
                COUNT(*) as total_reservas,
                COUNT(DISTINCT nombre_sala) as salas_utilizadas,
                COUNT(DISTINCT edificio) as edificios_utilizados
            FROM reserva
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY mes
            ORDER BY mes DESC
        """
        return fetch_query(query)
    
    @staticmethod
    def ranking_usuarios_activos():
        """
        Consulta adicional 3: Top usuarios más activos (mayor cantidad de reservas)
        """
        query = """
            SELECT 
                p.ci,
                p.nombre,
                p.apellido,
                ppa.rol,
                pa.tipo as tipo_programa,
                COUNT(DISTINCT r.id_reserva) as total_reservas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) as asistencias,
                COUNT(DISTINCT s.id_sancion) as sanciones
            FROM participante p
            JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            LEFT JOIN reserva_participante rp ON p.ci = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            LEFT JOIN sancion_participante s ON p.ci = s.ci_participante
            GROUP BY p.ci, p.nombre, p.apellido, ppa.rol, pa.tipo
            HAVING total_reservas > 0
            ORDER BY total_reservas DESC
            LIMIT 20
        """
        return fetch_query(query)