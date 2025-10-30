from app.database import fetch_query

class Sala:
    @staticmethod
    def get_all():
        """Obtiene todas las salas con información del edificio"""
        query = """
            SELECT s.*, e.direccion, e.departamento
            FROM sala s
            JOIN edificio e ON s.edificio = e.nombre_edificio
            ORDER BY s.edificio, s.nombre_sala
        """
        return fetch_query(query)
    
    @staticmethod
    def get_by_nombre_edificio(nombre_sala, edificio):
        """Obtiene una sala específica dado su nombre y edificio"""
        query = """
            SELECT s.*, e.direccion, e.departamento
            FROM sala s
            JOIN edificio e ON s.edificio = e.nombre_edificio
            WHERE s.nombre_sala = %s AND s.edificio = %s
        """
        rows = fetch_query(query, (nombre_sala, edificio))
        return rows[0] if rows else None
    
    @staticmethod
    def get_disponibles(fecha, id_turno, ci_participante):
        """
        Obtiene salas disponibles para una fecha y turno específicos
        Filtra según permisos del participante
        """
        from app.models.participante import Participante
        
        # Obtener información del participante
        participante = Participante.get_by_ci(ci_participante)
        if not participante: #si no existe el participante
            return []
        
        #se consulta el rol academico
        es_docente = Participante.es_docente(ci_participante)
        es_posgrado = Participante.es_posgrado(ci_participante)
        
        # Construir condición de tipo de sala según permisos
        if es_docente:
            tipo_condicion = "s.tipo_sala IN ('libre', 'docente', 'posgrado')"
        elif es_posgrado:
            tipo_condicion = "s.tipo_sala IN ('libre', 'posgrado')"
        else:
            tipo_condicion = "s.tipo_sala = 'libre'"
        
        query = f"""
            SELECT s.*, e.direccion, e.departamento,
                   CASE WHEN r.id_reserva IS NULL THEN 1 ELSE 0 END as disponible
            FROM sala s
            JOIN edificio e ON s.edificio = e.nombre_edificio
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala 
                                AND s.edificio = r.edificio
                                AND r.fecha = %s
                                AND r.id_turno = %s
                                AND r.estado = 'activa'
            WHERE {tipo_condicion}
            HAVING disponible = 1
            ORDER BY s.edificio, s.nombre_sala
        """
        return fetch_query(query, (fecha, id_turno))
    
    @staticmethod
    def puede_reservar(nombre_sala, edificio, ci_participante):
        """Verifica si un participante tiene el permiso para poder  reservar una sala específica"""
        from app.models.participante import Participante
        
        sala = Sala.get_by_nombre_edificio(nombre_sala, edificio) #se obtiene la sala
        if not sala:
            return False, "Sala no encontrada"
        #comprobar rol del paticipante
        es_docente = Participante.es_docente(ci_participante)
        es_posgrado = Participante.es_posgrado(ci_participante)
        
        tipo = sala['tipo_sala']
        
        if tipo == 'libre':
            return True, "OK"
        elif tipo == 'docente':
            if es_docente:
                return True, "OK"
            return False, "Solo docentes pueden reservar esta sala"
        elif tipo == 'posgrado':
            if es_docente or es_posgrado:
                return True, "OK"
            return False, "Solo docentes o estudiantes de posgrado pueden reservar esta sala"
        
        return False, "Tipo de sala desconocido"