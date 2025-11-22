from app.database import fetch_query, execute_query

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
        Obtiene las salas disponibles para una fecha y turno específicos,
        filtrando según permisos del participante.
        """
        from app.models.participante import Participante

        # Obtener información del participante
        participante = Participante.get_by_ci(ci_participante)
        if not participante:
            return []

        # Verificar rol académico
        es_docente = Participante.es_docente(ci_participante)
        es_posgrado = Participante.es_posgrado(ci_participante)

        # Construir condición de tipo de sala según permisos
        if es_docente:
            tipo_condicion = "s.tipo_sala IN ('libre', 'docente')"
        elif es_posgrado:
            tipo_condicion = "s.tipo_sala IN ('libre', 'posgrado')"
        else:
            tipo_condicion = "s.tipo_sala = 'libre'"

        query = f"""
            SELECT 
                s.nombre_sala,
                s.edificio,
                s.capacidad,
                s.tipo_sala,
                e.direccion,
                e.departamento
            FROM sala s
            JOIN edificio e ON s.edificio = e.nombre_edificio
            LEFT JOIN reserva r 
                ON r.nombre_sala = s.nombre_sala
                AND r.edificio = s.edificio
                AND r.fecha = %s
                AND r.id_turno = %s
                AND r.estado = 'activa'
            WHERE 
                {tipo_condicion}
                AND r.id_reserva IS NULL   -- clave: solo salas sin reserva activa
            ORDER BY s.edificio, s.nombre_sala;
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
            if es_posgrado:
                return True, "OK"
            return False, "Solo docentes o estudiantes de posgrado pueden reservar esta sala"
        
        return False, "Tipo de sala desconocido"

    @staticmethod
    def crear(nombre_sala, edificio, capacidad, tipo_sala):
        """Crea una nueva sala"""
        try:
            query = """
                INSERT INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
                VALUES (%s, %s, %s, %s)
            """
            execute_query(query, (nombre_sala, edificio, capacidad, tipo_sala))
            return True, "Sala creada exitosamente"
        except Exception as e:
            return False, f"Error al crear sala: {str(e)}"

    @staticmethod
    def actualizar(nombre_sala, edificio, capacidad, tipo_sala):
        """Actualiza una sala existente (solo capacidad y tipo)"""
        try:
            query = """
                UPDATE sala
                SET capacidad = %s, tipo_sala = %s
                WHERE nombre_sala = %s AND edificio = %s
            """
            execute_query(query, (capacidad, tipo_sala, nombre_sala, edificio))
            return True, "Sala actualizada exitosamente"
        except Exception as e:
            return False, f"Error al actualizar sala: {str(e)}"

    @staticmethod
    def eliminar(nombre_sala, edificio):
        """Elimina una sala (solo si no tiene reservas asociadas)"""
        try:
            # Verificar si tiene reservas asociadas
            check_query = """
                SELECT COUNT(*) as count FROM reserva
                WHERE nombre_sala = %s AND edificio = %s
            """
            result = fetch_query(check_query, (nombre_sala, edificio))
            if result and result[0]['count'] > 0:
                return False, "No se puede eliminar una sala con reservas asociadas"

            query = "DELETE FROM sala WHERE nombre_sala = %s AND edificio = %s"
            execute_query(query, (nombre_sala, edificio))
            return True, "Sala eliminada exitosamente"
        except Exception as e:
            return False, f"Error al eliminar sala: {str(e)}"