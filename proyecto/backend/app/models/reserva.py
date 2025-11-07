from app.database import fetch_query, execute_query
from datetime import date

class Reserva:
    @staticmethod
    def get_by_participante(ci_participante, incluir_canceladas=False):
        """Obtiene todas las reservas de un participante, opcionalmente incluyendo las canceladas"""
        estado_condicion = "" if incluir_canceladas else "AND r.estado != 'cancelada'"
        
        query = f"""
            SELECT r.*, 
                   rp.fecha_solicitud_reserva, rp.asistencia,
                   s.capacidad, s.tipo_sala,
                   e.direccion, e.departamento,
                   t.hora_inicio, t.hora_fin,
                   p.nombre, p.apellido
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
            JOIN edificio e ON s.edificio = e.nombre_edificio
            JOIN turno t ON r.id_turno = t.id_turno
            JOIN participante p ON rp.ci_participante = p.ci
            WHERE rp.ci_participante = %s
            {estado_condicion}
            ORDER BY r.fecha DESC, t.hora_inicio DESC
        """
        return fetch_query(query, (ci_participante,))
    
    @staticmethod
    def get_by_id(id_reserva):
        """Obtiene una reserva específica con toda su información a partir del id de la reserva"""
        query = """
            SELECT r.*, 
                   rp.ci_participante, rp.fecha_solicitud_reserva, rp.asistencia,
                   s.capacidad, s.tipo_sala,
                   e.direccion, e.departamento,
                   t.hora_inicio, t.hora_fin,
                   p.nombre, p.apellido, p.email
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
            JOIN edificio e ON s.edificio = e.nombre_edificio
            JOIN turno t ON r.id_turno = t.id_turno
            JOIN participante p ON rp.ci_participante = p.ci
            WHERE r.id_reserva = %s
        """
        rows = fetch_query(query, (id_reserva,)) 
        return rows[0] if rows else None # si la reserva existe, devuelve  el único diccionario, sino devuelve None
    
    @staticmethod
    def crear(nombre_sala, edificio, fecha, id_turno, ci_participante):
        """Crea una nueva reserva TODAS las validaciones"""
        from app.models.validaciones import ValidacionesReserva
        
        # Validar TODAS las reglas de forma centralizadas
        puede, mensaje = ValidacionesReserva.puede_reservar(
            ci_participante, nombre_sala, edificio, fecha, id_turno
        )
        
        if not puede:
            return None, mensaje
        
        # Verificar que la sala esté disponible en ese turno
        query_check = """
            SELECT COUNT(*) as count FROM reserva
            WHERE nombre_sala = %s AND edificio = %s 
            AND fecha = %s AND id_turno = %s AND estado = 'activa'
        """
        rows = fetch_query(query_check, (nombre_sala, edificio, fecha, id_turno))
        if rows and rows[0]['count'] > 0:
            return None, "La sala ya está reservada en ese turno"
        
        # Crear la reserva
        query_reserva = """
            INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
            VALUES (%s, %s, %s, %s, 'activa')
        """
        if not execute_query(query_reserva, (nombre_sala, edificio, fecha, id_turno)):
            return None, "Error al crear la reserva"
        
        # Obtener el ID de la reserva recién creada
        query_last_id = "SELECT LAST_INSERT_ID() as id"
        rows = fetch_query(query_last_id)
        if not rows:
            return None, "Error al obtener ID de reserva"
        
        id_reserva = rows[0]['id']
        
        # Crear la relación reserva-participante
        query_participante = """
            INSERT INTO reserva_participante (ci_participante, id_reserva, fecha_solicitud_reserva, asistencia)
            VALUES (%s, %s, %s, 0)
        """
        fecha_hoy = date.today()
        if not execute_query(query_participante, (ci_participante, id_reserva, fecha_hoy)):
            return None, "Error al asociar participante a la reserva"
        
        return id_reserva, "Reserva creada exitosamente"
    
    @staticmethod
    def cancelar(id_reserva, ci_participante):
        """Cancela una reserva (solo si es del participante y está activa)"""
        reserva = Reserva.get_by_id(id_reserva) 
        #verifica que exista la reserva
        if not reserva:
            return False, "Reserva no encontrada"
        #verifica que la reserva sea propia
        if reserva['ci_participante'] != ci_participante:
            return False, "No tienes permiso para cancelar esta reserva"
        #verifica que la reserva  no este cancelada
        if reserva['estado'] != 'activa':
            return False, f"No se puede cancelar una reserva con estado '{reserva['estado']}'"
        
        # No permitir cancelar reservas pasadas
        if reserva['fecha'] < date.today():
            return False, "No se pueden cancelar reservas pasadas"
        
        #Actualizar el estado de la reserva
        query = """
            UPDATE reserva 
            SET estado = 'cancelada'
            WHERE id_reserva = %s
        """
        if execute_query(query, (id_reserva,)):
            return True, "Reserva cancelada exitosamente" #La reserva fue cancelada
        return False, "Error al cancelar la reserva" #No se pudo cancelar la reserva
    
    @staticmethod
    def get_activas_futuras(ci_participante):
        """Obtiene las reservas activas futuras de un participante"""
        query = """
            SELECT r.*, 
                   s.capacidad, s.tipo_sala,
                   e.direccion, e.departamento,
                   t.hora_inicio, t.hora_fin
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
            JOIN edificio e ON s.edificio = e.nombre_edificio
            JOIN turno t ON r.id_turno = t.id_turno
            WHERE rp.ci_participante = %s
            AND r.estado = 'activa'
            AND r.fecha >= CURDATE()
            ORDER BY r.fecha, t.hora_inicio
        """
        return fetch_query(query, (ci_participante,))