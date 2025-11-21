from app.database import fetch_query, execute_query

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

    @staticmethod
    def crear(hora_inicio, hora_fin):
        """Crea un nuevo turno"""
        try:
            query = "INSERT INTO turno (hora_inicio, hora_fin) VALUES (%s, %s)"
            execute_query(query, (hora_inicio, hora_fin))
            return True, "Turno creado exitosamente"
        except Exception as e:
            return False, f"Error al crear turno: {str(e)}"

    @staticmethod
    def actualizar(id_turno, hora_inicio, hora_fin):
        """Actualiza un turno existente"""
        try:
            query = "UPDATE turno SET hora_inicio = %s, hora_fin = %s WHERE id_turno = %s"
            execute_query(query, (hora_inicio, hora_fin, id_turno))
            return True, "Turno actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar turno: {str(e)}"

    @staticmethod
    def eliminar(id_turno):
        """Elimina un turno (solo si no tiene reservas asociadas)"""
        try:
            # Verificar si tiene reservas asociadas
            check_query = "SELECT COUNT(*) as count FROM reserva WHERE id_turno = %s"
            result = fetch_query(check_query, (id_turno,))
            if result and result[0]['count'] > 0:
                return False, "No se puede eliminar un turno con reservas asociadas"

            query = "DELETE FROM turno WHERE id_turno = %s"
            execute_query(query, (id_turno,))
            return True, "Turno eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar turno: {str(e)}"