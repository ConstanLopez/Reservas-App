from app.database import fetch_query, execute_query
from datetime import date,timedelta
from app.models.participante import Participante
from app.models.sala import Sala
from app.models.turno import Turno
class Reserva:
    @staticmethod
    def get_by_participante(ci_participante, incluir_canceladas=False):
        """Obtiene todas las reservas de un participante, con TODOS sus participantes"""
        estado_condicion = "" if incluir_canceladas else "AND r.estado != 'cancelada'"
        
        query = f"""
            SELECT r.*, 
                TIME_FORMAT(r.hora_inicio_rango, '%H:%i') AS hora_inicio_rango,
                TIME_FORMAT(r.hora_fin_rango, '%H:%i')   AS hora_fin_rango,
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
        rows = fetch_query(query, (ci_participante,))

        # 👉 Para cada reserva, adjuntamos la lista completa de participantes
        for r in rows:
            r['participantes'] = Reserva.get_participantes_de_reserva(r['id_reserva'])

        return rows
    

    @staticmethod
    def get_participantes_de_reserva(id_reserva):
        query = """
            SELECT 
                rp.ci_participante AS ci,
                COALESCE(p.nombre, rp.nombre_invitado) AS nombre,
                COALESCE(p.apellido, rp.apellido_invitado) AS apellido,
                p.email
            FROM reserva_participante rp
            LEFT JOIN participante p ON p.ci = rp.ci_participante
            WHERE rp.id_reserva = %s
            ORDER BY nombre, apellido
        """
        return fetch_query(query, (id_reserva,))
    
    @staticmethod
    def get_by_id(id_reserva):
        """Obtiene una reserva específica con toda su información a partir del id de la reserva"""
        query = """
            SELECT r.*, 
                    TIME_FORMAT(r.hora_inicio_rango, '%H:%i') AS hora_inicio_rango,
                    TIME_FORMAT(r.hora_fin_rango, '%H:%i')   AS hora_fin_rango,
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
    def crear(nombre_sala, edificio, fecha, id_turno, ci_participante,participantes=None,
          hora_inicio_rango=None, hora_fin_rango=None):
        """Crea una nueva reserva TODAS las validaciones"""
        from app.models.validaciones import ValidacionesReserva
        
        if participantes is None:
            participantes = []
        if not isinstance(participantes, list):
            participantes = []
        # Validar TODAS las reglas de forma centralizadas
        puede, mensaje = ValidacionesReserva.puede_reservar(
            ci_participante, nombre_sala, edificio, fecha, id_turno
        )
        
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
            if (es_docente and tipo_sala == 'docente') or (es_posgrado and tipo_sala == 'posgrado'):
                aplica_limites = False

        # Si le aplican los límites, controlamos cuántas horas tiene ya reservadas ese día
                # Si le aplican los límites, controlamos cuántas horas tiene ya reservadas
        if aplica_limites:
            # Traemos todas las reservas de este participante (con tipo_sala incluido)
            reservas_participante = Reserva.get_by_participante(ci_participante)

            def _horas_entre(hora_ini_str, hora_fin_str):
                h1, m1 = map(int, hora_ini_str.split(':'))
                h2, m2 = map(int, hora_fin_str.split(':'))
                return (h2*60 + m2 - (h1*60 + m1)) / 60.0

            # --- NUEVO: decidir qué reservas cuentan para los límites ---
            def _cuenta_para_limites(r):
                ts = r.get('tipo_sala')

                # Docente: las salas 'docente' NO cuentan para los límites
                if es_docente and ts == 'docente':
                    return False

                # Alumno de posgrado: las salas 'posgrado' NO cuentan
                if es_posgrado and ts == 'posgrado':
                    return False

                # El resto de las salas sí cuentan
                return True

            # 1) Horas ya reservadas ese día (solo reservas que cuentan)
            reservas_mismo_dia = [
                r for r in reservas_participante
                if r['fecha'] == fecha
                   and r['estado'] == 'activa'
                   and _cuenta_para_limites(r)
            ]

            horas_reservadas = 0.0
            for r in reservas_mismo_dia:
                if r.get('hora_inicio_rango') and r.get('hora_fin_rango'):
                    horas_reservadas += _horas_entre(
                        r['hora_inicio_rango'],
                        r['hora_fin_rango']
                    )
                else:
                    horas_reservadas += _horas_entre(
                        r['hora_inicio'],
                        r['hora_fin']
                    )

            # 2) Horas de la nueva reserva (sea rango o turno)
            if hora_inicio_rango and hora_fin_rango:
                horas_nueva = _horas_entre(hora_inicio_rango, hora_fin_rango)
            else:
                turno = Turno.get_by_id(id_turno)
                horas_nueva = _horas_entre(
                    turno['hora_inicio'],
                    turno['hora_fin']
                )

            # 3) Validar máximo 2 horas por día
            if horas_reservadas + horas_nueva > 2:
                return None, "No puedes reservar más de 2 horas de sala en el mismo día."

            # 4) Validar máximo 3 reservas activas en la semana
            weekday = fecha.weekday()
            week_start = fecha - timedelta(days=weekday)   # lunes
            week_end   = week_start + timedelta(days=6)    # domingo

            reservas_misma_semana = [
                r for r in reservas_participante
                if week_start <= r['fecha'] <= week_end
                   and r['estado'] == 'activa'
                   and _cuenta_para_limites(r)
            ]

            reservas_activas_semana = len(reservas_misma_semana)

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
            INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado,hora_inicio_rango, hora_fin_rango)
            VALUES (%s, %s, %s, %s, 'activa', %s, %s)
        """
        if not execute_query(query_reserva, (nombre_sala, edificio, fecha, id_turno,hora_inicio_rango, hora_fin_rango)):
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
        
        query_extra_registrado = """
            INSERT INTO reserva_participante 
                (ci_participante, id_reserva, fecha_solicitud_reserva, asistencia)
            VALUES (%s, %s, %s, 0)
        """

        query_extra_invitado = """
            INSERT INTO reserva_participante 
                (ci_participante, id_reserva, fecha_solicitud_reserva, asistencia,
                 nombre_invitado, apellido_invitado)
            VALUES (%s, %s, %s, 0, %s, %s)
        """

        for p in participantes:
            # p viene como dict {ci: "...", nombre: "..."} desde el front
            if isinstance(p, dict):
                ci_extra = (p.get('ci') or '').strip()
                nombre_completo = (p.get('nombre') or '').strip()
            else:
                # si llegara algo raro, lo ignoramos
                continue

            # si viene vacío, lo saltamos
            if not ci_extra:
                continue

            # no duplicar al responsable
            if ci_extra == str(ci_participante):
                continue

            # ¿Existe ya como participante registrado?
            fila_participante = Participante.get_by_ci(ci_extra)

            if fila_participante:
                # Es alguien que ya está en la tabla participante
                execute_query(
                    query_extra_registrado,
                    (ci_extra, id_reserva, fecha_hoy)
                )
            else:
                # Invitado que no está en participante → guardamos su nombre acá
                if ' ' in nombre_completo:
                    nombre_inv, apellido_inv = nombre_completo.split(' ', 1)
                else:
                    nombre_inv, apellido_inv = nombre_completo, ''

                execute_query(
                    query_extra_invitado,
                    (ci_extra, id_reserva, fecha_hoy, nombre_inv, apellido_inv)
                )

        return id_reserva, "Reserva creada exitosamente"
    
    @staticmethod
    def cancelar(id_reserva, ci_participante):
        """
        Cancela una reserva (solo si el usuario es participante y está activa)
        """
        # 1) Traer la reserva
        query_reserva = """
            SELECT *
            FROM reserva
            WHERE id_reserva = %s
        """
        rows = fetch_query(query_reserva, (id_reserva,))
        if not rows:
            return False, "Reserva no encontrada"

        reserva = rows[0]

        # 2) Verificar que el usuario sea uno de los participantes de esa reserva
        participantes = Reserva.get_participantes_de_reserva(id_reserva)
        es_participante = any(
            str(p["ci"]) == str(ci_participante) 
            for p in participantes
        )

        if not es_participante:
            return False, "No tienes permiso para cancelar esta reserva"

        # 3) Verificar estado de la reserva
        if reserva['estado'] != 'activa':
            return False, f"No se puede cancelar una reserva con estado '{reserva['estado']}'"

        # 4) No permitir cancelar reservas pasadas
        if reserva['fecha'] < date.today():
            return False, "No se pueden cancelar reservas pasadas"

        # 5) Actualizar el estado a cancelada
        query_update = """
            UPDATE reserva 
            SET estado = 'cancelada'
            WHERE id_reserva = %s
        """
        if execute_query(query_update, (id_reserva,)):
            return True, "Reserva cancelada exitosamente"

        return False, "Error al cancelar la reserva"
    
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
        try:
            campos, valores = [], []
            for key, val in data.items():
                if key != 'id_reserva':  # No actualizar la PK
                    campos.append(f"{key} = %s")
                    valores.append(val)
            if not campos:
                return True, "No hay campos para actualizar"
            valores.append(id_reserva)
            query = f"UPDATE reserva SET {', '.join(campos)} WHERE id_reserva = %s"
            ok = execute_query(query, tuple(valores))
            return ok, "Reserva actualizada correctamente"
        except Exception as e:
            return False, f"Error al actualizar reserva: {str(e)}"

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