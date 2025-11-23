from flask import Blueprint, jsonify
from app.middleware.auth_middleware import token_required
from app.models.reportes import Reportes

bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')

@bp.get('/salas-mas-reservadas')
@token_required
def get_salas_mas_reservadas(current_user):
    """Obtiene las salas más reservadas"""
    try:
        limit = 10  # Definimos mostrar las 10 salas mas reservadas
        datos = Reportes.salas_mas_reservadas(limit)
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/turnos-mas-demandados')
@token_required
def get_turnos_mas_demandados(current_user):
    """Obtiene los turnos más demandados"""
    try:
        datos = Reportes.turnos_mas_demandados()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/promedio-participantes')
@token_required
def get_promedio_participantes(current_user):
    """Obtiene el promedio de participantes por sala"""
    try:
        datos = Reportes.promedio_participantes_por_sala()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/reservas-por-carrera')
@token_required
def get_reservas_por_carrera(current_user):
    """Obtiene reservas agrupadas por carrera y facultad"""
    try:
        datos = Reportes.reservas_por_carrera_y_facultad()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/ocupacion-por-edificio')
@token_required
def get_ocupacion_por_edificio(current_user):
    """Obtiene el porcentaje de ocupación por edificio"""
    try:
        datos = Reportes.porcentaje_ocupacion_por_edificio()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/reservas-por-rol')
@token_required
def get_reservas_por_rol(current_user):
    """Obtiene reservas y asistencias por rol"""
    try:
        datos = Reportes.reservas_y_asistencias_por_rol()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/sanciones-por-rol')
@token_required
def get_sanciones_por_rol(current_user):
    """Obtiene cantidad de sanciones por rol"""
    try:
        datos = Reportes.cantidad_sanciones_por_rol()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/efectividad-reservas')
@token_required
def get_efectividad_reservas(current_user):
    """Obtiene porcentaje de reservas utilizadas vs canceladas"""
    try:
        datos = Reportes.efectividad_reservas()
        return jsonify({
            'success': True,
            'data': datos
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/horarios-pico')
@token_required
def get_horarios_pico(current_user):
    """Consulta adicional: Horarios de mayor demanda"""
    try:
        datos = Reportes.horarios_pico()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/tendencia-mensual')
@token_required
def get_tendencia_mensual(current_user):
    """Consulta adicional: Tendencia de uso mensual"""
    try:
        datos = Reportes.tendencia_uso_mensual()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/usuarios-activos')
@token_required
def get_usuarios_activos(current_user):
    """Consulta adicional: Top usuarios más activos"""
    try:
        datos = Reportes.ranking_usuarios_activos()
        return jsonify({
            'success': True,
            'data': datos,
            'count': len(datos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/dashboard-completo')
@token_required
def get_dashboard_completo(current_user):
    """Obtiene un resumen de todos los reportes para dashboard"""
    try:
        dashboard = {
            'salas_top': Reportes.salas_mas_reservadas(5),
            'turnos_demandados': Reportes.turnos_mas_demandados(),
            'efectividad': Reportes.efectividad_reservas(),
            'ocupacion_edificios': Reportes.porcentaje_ocupacion_por_edificio(),
            'horarios_pico': Reportes.horarios_pico()
        }
        return jsonify({
            'success': True,
            'data': dashboard
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500