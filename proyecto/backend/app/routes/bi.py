from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import admin_required
from app.database import fetch_query
from flask_cors import cross_origin

bp = Blueprint('bi', __name__, url_prefix='/api/bi')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# CONSULTA 1: Ocupación de salas por edificio
# Muestra cuántas reservas activas tiene cada sala agrupadas por edificio
@bp.route('/ocupacion-salas', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def ocupacion_salas(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        query = """
            SELECT
                s.edificio,
                s.nombre_sala,
                s.capacidad,
                s.tipo_sala,
                COUNT(r.id_reserva) as total_reservas,
                SUM(CASE WHEN r.estado = 'activa' THEN 1 ELSE 0 END) as reservas_activas
            FROM sala s
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala
                               AND s.edificio = r.edificio
            GROUP BY s.edificio, s.nombre_sala, s.capacidad, s.tipo_sala
            ORDER BY s.edificio, total_reservas DESC
        """
        result = fetch_query(query)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CONSULTA 2: Reservas por participante
# Muestra cantidad de reservas por usuario con su estado
@bp.route('/reservas-por-participante', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def reservas_por_participante(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        query = """
            SELECT
                p.ci,
                p.nombre,
                p.apellido,
                p.email,
                COUNT(DISTINCT rp.id_reserva) as total_reservas,
                SUM(CASE WHEN r.estado = 'activa' THEN 1 ELSE 0 END) as activas,
                SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
                SUM(CASE WHEN r.estado = 'sin asistencia' THEN 1 ELSE 0 END) as sin_asistencia,
                SUM(CASE WHEN r.estado = 'finalizada' THEN 1 ELSE 0 END) as finalizadas
            FROM participante p
            LEFT JOIN reserva_participante rp ON p.ci = rp.ci_participante
            LEFT JOIN reserva r ON rp.id_reserva = r.id_reserva
            GROUP BY p.ci, p.nombre, p.apellido, p.email
            ORDER BY total_reservas DESC
        """
        result = fetch_query(query)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CONSULTA 3: Turnos más solicitados
# Muestra qué horarios tienen más demanda
@bp.route('/turnos-populares', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def turnos_populares(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        query = """
            SELECT
                t.id_turno,
                TIME_FORMAT(t.hora_inicio, '%H:%i') as hora_inicio,
                TIME_FORMAT(t.hora_fin, '%H:%i') as hora_fin,
                COUNT(r.id_reserva) as total_reservas,
                SUM(CASE WHEN r.estado = 'activa' THEN 1 ELSE 0 END) as activas
            FROM turno t
            LEFT JOIN reserva r ON t.id_turno = r.id_turno
            GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
            ORDER BY total_reservas DESC
        """
        result = fetch_query(query)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CONSULTA 4: Tasa de asistencia
# Calcula porcentaje de asistencia vs inasistencia por participante
@bp.route('/tasa-asistencia', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def tasa_asistencia(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        query = """
            SELECT
                p.ci,
                p.nombre,
                p.apellido,
                COUNT(rp.id_reserva) as total_reservas_finalizadas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) as asistencias,
                SUM(CASE WHEN rp.asistencia = 0 THEN 1 ELSE 0 END) as inasistencias,
                ROUND(
                    (SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) * 100.0) /
                    NULLIF(COUNT(rp.id_reserva), 0),
                    2
                ) as porcentaje_asistencia
            FROM participante p
            LEFT JOIN reserva_participante rp ON p.ci = rp.ci_participante
            WHERE rp.id_reserva IS NOT NULL
            GROUP BY p.ci, p.nombre, p.apellido
            HAVING total_reservas_finalizadas > 0
            ORDER BY porcentaje_asistencia DESC
        """
        result = fetch_query(query)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CONSULTA 5: Sanciones activas
# Lista participantes con sanciones vigentes
@bp.route('/sanciones-activas', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def sanciones_activas(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        query = """
            SELECT
                p.ci,
                p.nombre,
                p.apellido,
                p.email,
                sp.fecha_inicio,
                sp.fecha_fin,
                DATEDIFF(sp.fecha_fin, CURDATE()) as dias_restantes
            FROM participante p
            INNER JOIN sancion_partcipante sp ON p.ci = sp.ci_participante
            WHERE sp.fecha_fin >= CURDATE()
            ORDER BY sp.fecha_fin ASC
        """
        result = fetch_query(query)
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CONSULTA 6: Reservas por rango de fechas
# Permite filtrar reservas por fecha de inicio y fin
@bp.route('/reservas-por-fecha', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def reservas_por_fecha(current_user):
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'message': 'Se requieren fecha_inicio y fecha_fin'
            }), 400

        query = """
            SELECT
                DATE(r.fecha) as fecha,
                COUNT(r.id_reserva) as total_reservas,
                SUM(CASE WHEN r.estado = 'activa' THEN 1 ELSE 0 END) as activas,
                SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
                SUM(CASE WHEN r.estado = 'finalizada' THEN 1 ELSE 0 END) as finalizadas
            FROM reserva r
            WHERE r.fecha BETWEEN %s AND %s
            GROUP BY DATE(r.fecha)
            ORDER BY fecha DESC
        """
        result = fetch_query(query, (fecha_inicio, fecha_fin))
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
