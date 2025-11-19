from app.database import fetch_query, execute_query
from datetime import date,timedelta
from app.models.participante import Participante

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
                   TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i')   AS hora_fin,
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
                   TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i')   AS hora_fin,
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
        """Crea una nueva reserva"""
        from app.models.participante import Participante
        from app.models.sala import Sala
        
        # Validar que el participante no tenga sanciones activas
        if Participante.tiene_sancion_activa(ci_participante):
            sancion = Participante.get_sancion_activa(ci_participante)
            return None, f"No puedes realizar reservas. Tienes una sanción activa hasta {sancion['fecha_fin']}"
        
        # Validar permisos sobre la sala
        puede, mensaje = Sala.puede_reservar(nombre_sala, edificio, ci_participante)
        if not puede:
            return None, mensaje

        #Flags para ver si aplica la regla de limite horario para las reservas
        es_docente = Participante.es_docente(ci_participante)
        es_posgrado = Participante.es_posgrado(ci_participante)
        sala = Sala.get_by_nombre_edificio(nombre_sala, edificio)

        aplica_limites = True 

        if sala:
            tipo_sala = sala['tipo_sala']  # 'libre', 'docente', 'posgrado'
            
            # Si es docente o posgrado Y está usando sala exclusiva (docente/posgrado),
            # NO se aplican los límites de 2 horas ni de 3 reservas.
            if (es_docente or es_posgrado) and tipo_sala in ('docente', 'posgrado'):
                aplica_limites = False

        # Si le aplican los límites, controlamos cuántas horas tiene ya reservadas ese día
        if aplica_limites:
            # Traemos todas las reservas  de este participante
            reservas_participante = Reserva.get_by_participante(ci_participante)

            # Filtramos solo las reservas de la misma fecha  y que esten  activas
            reservas_mismo_dia = [
                r for r in reservas_participante
                if r['fecha'] == fecha and r['estado'] == 'activa'
            ]

            # Cada reserva  vale 1 hora (1 turno = 1 hora)
            horas_reservadas = len(reservas_mismo_dia)

            # Si ya tiene 2 horas, No se puede realizar una tercera
            if horas_reservadas >= 2:
                return None, "No puedes reservar más de 2 horas de sala en el mismo día."
            
            weekday = fecha.weekday()
            week_start = fecha - timedelta(days=weekday)        # lunes de esa semana
            week_end = week_start + timedelta(days=6)           # domingo de esa semana

            # Filtramos las reservas de ese participante que caen en esa semana y están activas
            reservas_misma_semana = [
                r for r in reservas_participante
                if (week_start <= r['fecha'] <= week_end) and r['estado'] == 'activa'
            ]

            reservas_activas_semana = len(reservas_misma_semana)

            # Si ya tiene 3 reservas activas en esa semana, no permitimos una nueva
            if reservas_activas_semana >= 3:
                return None, "No puedes tener más de 3 reservas activas en la misma semana."

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
        query_last_id = """
            SELECT id_reserva AS id
            FROM reserva
            WHERE nombre_sala = %s AND edificio = %s AND fecha = %s AND id_turno = %s
            ORDER BY id_reserva DESC
            LIMIT 1
        """
        rows = fetch_query(query_last_id, (nombre_sala, edificio, fecha, id_turno))
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
                   TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i')   AS hora_fin,
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
    
    @staticmethod
    def registrar_asistencia(id_reserva, asistencias):
        """
        Actualiza asistencia de todos los participantes de una reserva.
        Si nadie asistió, genera sanciones de 2 meses para todos.
        """
        # 1) Traer todos los participantes de esa reserva
        query_participantes = """
            SELECT ci_participante
            FROM reserva_participante
            WHERE id_reserva = %s
        """
        rows = fetch_query(query_participantes, (id_reserva,))
        if not rows:
            return False, "No se encontraron participantes para esta reserva."

        # Convertir la lista de asistencias del request a algo fácil de consultar
        # ejemplo: {"12345678": True, "87654321": False}
        mapa_asistencias = {a["ci"]: bool(a.get("asistio", False)) for a in asistencias}

        # 2) Actualizar asistencia en reserva_participante
        hubo_asistencia = False
        for row in rows:
            ci = row["ci_participante"]
            asistio = mapa_asistencias.get(ci, False)  # si no vino en el JSON, asumimos False

            query_update = """
                UPDATE reserva_participante
                SET asistencia = %s
                WHERE id_reserva = %s AND ci_participante = %s
            """
            execute_query(query_update, (1 if asistio else 0, id_reserva, ci))

            if asistio:
                hubo_asistencia = True

        # 3) Si al menos uno asistió, no hay sanciones
            if hubo_asistencia:
                return True, "Asistencia registrada correctamente. No se generaron sanciones."

        # 4) Si nadie asistió → sanción de 2 meses para todos los participantes
        from datetime import date, timedelta
        fecha_inicio = date.today()
        # Súper simple: 60 días como aproximación a 2 meses
        fecha_fin = fecha_inicio + timedelta(days=60)

        for row in rows:
            ci = row["ci_participante"]

            query_sancion = """
                INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s)
            """
            execute_query(query_sancion, (ci, fecha_inicio, fecha_fin))

        return True, "Asistencia registrada. No asistió nadie, se generaron sanciones por 2 meses."
    
    @staticmethod
    def actualizar_por_admin(id_reserva, data):
        campos, valores = [], []
        for key, val in data.items():
            campos.append(f"{key} = %s")
            valores.append(val)
        valores.append(id_reserva)
        query = f"UPDATE reserva SET {', '.join(campos)} WHERE id_reserva = %s"
        ok = execute_query(query, tuple(valores))
        return ok, "Reserva actualizada correctamente"

    @staticmethod
    def cancelar_por_admin(id_reserva):
        query = "UPDATE reserva SET estado = 'cancelada_admin' WHERE id_reserva = %s"
        return execute_query(query, (id_reserva,)), "Reserva cancelada por administrador"
    
    @staticmethod
    def eliminar_por_admin(id_reserva):
        query = "DELETE FROM reserva WHERE id_reserva = %s"
        return execute_query(query, (id_reserva,)), "Reserva eliminada por administrador"
        
    @staticmethod
    def get_all():
        """Obtiene todas las reservas con información detallada"""
        query = """
            SELECT r.*, 
                   rp.ci_participante, rp.fecha_solicitud_reserva, rp.asistencia,
                   s.capacidad, s.tipo_sala,
                   e.direccion, e.departamento,
                   TIME_FORMAT(t.hora_inicio, '%H:%i') AS hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i')   AS hora_fin,
                   p.nombre, p.apellido, p.email
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
            JOIN edificio e ON s.edificio = e.nombre_edificio
            JOIN turno t ON r.id_turno = t.id_turno
            JOIN participante p ON rp.ci_participante = p.ci
            ORDER BY r.fecha DESC, t.hora_inicio DESC
        """
        return fetch_query(query)