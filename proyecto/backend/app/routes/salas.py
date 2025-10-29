from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import token_required
from app.models.sala import Sala
from datetime import datetime

bp = Blueprint('salas', __name__, url_prefix='/api/salas')

@bp.get('')
@token_required
def get_salas(current_user):
    """Obtiene todas las salas"""
    try:
        salas = Sala.get_all()
        return jsonify({
            'success': True,
            'data': salas,
            'count': len(salas)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/disponibles')
@token_required
def get_salas_disponibles(current_user):
    """
    Obtiene salas disponibles para una fecha y turno específicos
    Query params: fecha (YYYY-MM-DD), id_turno
    """
    try:
        fecha_str = request.args.get('fecha')
        id_turno = request.args.get('id_turno')
        
        if not fecha_str or not id_turno:
            return jsonify({
                'success': False,
                'message': 'Se requieren los parámetros: fecha e id_turno'
            }), 400
        
        # Validar formato de fecha
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        # Validar que no sea fecha pasada
        if fecha < datetime.now().date():
            return jsonify({
                'success': False,
                'message': 'No se pueden buscar salas para fechas pasadas'
            }), 400
        
        ci = current_user['ci']
        salas = Sala.get_disponibles(fecha, id_turno, ci)
        
        return jsonify({
            'success': True,
            'data': salas,
            'count': len(salas)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/<nombre_sala>/<edificio>')
@token_required
def get_sala_detalle(current_user, nombre_sala, edificio):
    """Obtiene el detalle de una sala específica"""
    try:
        sala = Sala.get_by_nombre_edificio(nombre_sala, edificio)
        
        if not sala:
            return jsonify({'success': False, 'message': 'Sala no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': sala
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500