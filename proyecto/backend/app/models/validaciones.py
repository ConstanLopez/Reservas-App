from app.database import fetch_query
from datetime import datetime, timedelta

class ValidacionesReserva:
    """
    Validaciones de reglas de negocio para reservas según especificaciones:
    - No más de 2 horas diarias por edificio (excepto docentes/posgrado en salas exclusivas)
    - No más de 3 reservas activas en una semana (excepto docentes/posgrado en salas exclusivas)
    - Docentes y posgrado no tienen limitaciones en salas exclusivas
    - Capacidad de sala
    - Participantes sancionados no pueden reservar
    """

    @staticmethod
    def puede_reservar(ci_participante, nombre_sala, edificio, fecha, id_turno):
        """
        Verifica todas las reglas de negocio antes de crear una reserva.
        Retorna (puede_reservar: bool, mensaje: str)
        """
        from app.models.participante import Participante
        from app.models.sala import Sala

        # Verificamos si tiene una sanción activa
        if Participante.tiene_sancion_activa(ci_participante):
            sancion = Participante.get_sancion_activa(ci_participante)
            return False, f"Tienes una sanción activa hasta {sancion['fecha_fin']}"

        # Obtenemos la  información de la sala
        sala = Sala.get_by_nombre_edificio(nombre_sala, edificio)
        if not sala:
            return False, "Sala no encontrada"

        # Verificar permisos sobre tipo de sala (libre, docente, posgrado)
        puede, mensaje = Sala.puede_reservar(nombre_sala, edificio, ci_participante)
        if not puede:
            return False, mensaje

        # Determinar si aplican restricciones
        es_docente = Participante.es_docente(ci_participante)
        es_posgrado = Participante.es_posgrado(ci_participante)
        sala_exclusiva = sala['tipo_sala'] in ['docente', 'posgrado']

        # Docentes y posgrado no tienen limitaciones en sus salas exclusivas
        if (es_docente and sala['tipo_sala'] == 'docente') or \
           ((es_docente or es_posgrado) and sala['tipo_sala'] == 'posgrado'):
            sin_restricciones = True
        else:
            sin_restricciones = False

        # Validaciones generales si no son docentes/posgrado en salas exclusivas
        if not sin_restricciones:
            # Límite de 2 horas diarias por edificio
            puede, mensaje = ValidacionesReserva._validar_limite_horas_diarias(
                ci_participante, edificio, fecha, id_turno
            )
            if not puede:
                return False, mensaje

            # Límite de 3 reservas activas por semana
            puede, mensaje = ValidacionesReserva._validar_limite_reservas_semanales(
                ci_participante
            )
            if not puede:
                return False, mensaje

        return True, "OK"

    @staticmethod
    def _validar_limite_horas_diarias(ci_participante, edificio, fecha, id_turno_nuevo):
        """
        Valida que el participante no exceda 2 horas en el mismo edificio en el mismo día.
        """
        query = """
            SELECT SUM(TIMESTAMPDIFF(HOUR, t.hora_inicio, t.hora_fin)) as horas_reservadas
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN turno t ON r.id_turno = t.id_turno
            WHERE rp.ci_participante = %s
            AND r.edificio = %s
            AND r.fecha = %s
            AND r.estado = 'activa'
        """
        rows = fetch_query(query, (ci_participante, edificio, fecha))
        horas_actuales = rows[0]['horas_reservadas'] or 0

        # Duración del nuevo turno
        query_turno = """
            SELECT TIMESTAMPDIFF(HOUR, hora_inicio, hora_fin) as duracion
            FROM turno
            WHERE id_turno = %s
        """
        turno = fetch_query(query_turno, (id_turno_nuevo,))
        duracion_nueva = turno[0]['duracion'] if turno else 1

        total = horas_actuales + duracion_nueva

        if total > 2:
            return False, f"Excedes el límite de 2 horas diarias en {edificio}. Tienes {horas_actuales}h reservadas"

        return True, "OK"

    @staticmethod
    def _validar_limite_reservas_semanales(ci_participante):
        """
        Valida que el participante no tenga más de 3 reservas activas en la semana actual.
        """
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  
        fin_semana = inicio_semana + timedelta(days=6)  

        query = """
            SELECT COUNT(*) as count
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            WHERE rp.ci_participante = %s
            AND r.estado = 'activa'
            AND r.fecha BETWEEN %s AND %s
        """
        rows = fetch_query(query, (ci_participante, inicio_semana, fin_semana))
        count = rows[0]['count'] if rows else 0

        if count >= 3:
            return False, "Ya tienes 3 reservas activas en esta semana. Cancela una o espera a la próxima semana"

        return True, "OK"

    @staticmethod
    def validar_capacidad_sala(nombre_sala, edificio, cantidad_participantes):
        """
        Valida que la cantidad de participantes no exceda la capacidad de la sala.
        """
        from app.models.sala import Sala

        sala = Sala.get_by_nombre_edificio(nombre_sala, edificio)
        if not sala:
            return False, "Sala no encontrada"

        if cantidad_participantes > sala['capacidad']:
            return False, f"La sala tiene capacidad para {sala['capacidad']} personas, solicitaste {cantidad_participantes}"

        return True, "OK"
