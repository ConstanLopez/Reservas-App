from app.database import fetch_query

class Turno:
    @staticmethod
    def get_all():
        """Obtiene todos los turnos ordenados por hora de inicio"""
        query = """
            SELECT 
                id_turno,
                TIME_FORMAT(hora_inicio, '%H:%i') AS hora_inicio,
                TIME_FORMAT(hora_fin, '%H:%i')   AS hora_fin
            FROM turno
            ORDER BY hora_inicio
        """
        return fetch_query(query)
    
    @staticmethod
    def get_by_id(id_turno):
        """Obtiene un turno específico por ID"""
        query = "SELECT * FROM turno WHERE id_turno = %s"
        rows = fetch_query(query, (id_turno,))
        return rows[0] if rows else None
    
    @staticmethod
    def get_disponibles_para_sala(fecha, nombre_sala, edificio):
        query = """
            SELECT 
                t.id_turno,
                TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                TIME_FORMAT(t.hora_fin, '%H:%i')   AS hora_fin,
                CASE WHEN r.id_reserva IS NULL THEN 1 ELSE 0 END as disponible
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
                                AND r.nombre_sala = %s
                                AND r.edificio = %s
                                AND r.fecha = %s
                                AND r.estado = 'activa'
            ORDER BY t.hora_inicio
        """
        return fetch_query(query, (nombre_sala, edificio, fecha))